import datetime
import base64
import io

import bcrypt
import pandas as pd
import streamlit as st

from PIL import Image
import card_decks as cd
import util_github as ghub

im = Image.open("baralhos.png")

# Load environment variables
tables_list = {
    "Tipos de baralhos": "types",
    "Temas": "themes", 
    "Jogos": "games", 
    "Cidades": "cities",
    "Paises": "countries", 
    "Coleções": "collections", 
    "Fabricantes": "manufacturers",
    "Número de cartas": "numbers"
}

tables_choice = {
    "Tipos de baralhos": "Tipo de baralho",
    "Temas": "Tema", 
    "Jogos": "Tipo de jogo", 
    "Cidades": "Cidade",
    "Paises": "País", 
    "Coleções": "Coleção", 
    "Fabricantes": "Fabricante",
    "Número de cartas": "Número de cartas"
}

# Initialize the app
st.set_page_config(page_title="Baralhos de Cartas", page_icon=im, layout="wide")

st.title("Baralhos de Cartas")
cd.init_db()

# Page configuration
PAGES = {
    "Ligar/Desligar": "login",
    "Listagens": "query",
    "Adicionar Baralhos ": "manage_decks",
    "Editar Baralhos ": "edit_decks",
    "Definições": "manage_tables"
}

# Inicialize a variável de estado apenas uma vez
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if 'edit_deck_id' not in st.session_state:
    st.session_state.edit_deck_id = 0

if 'choice_id' not in st.session_state:
    st.session_state.choice_id = 0

choice = st.sidebar.radio("Selecione uma opção", list(PAGES.keys()), index=st.session_state.choice_id)
index = 0

valid_password = st.secrets["VALID_PASSWORD"].encode('utf-8')
valid_username = st.secrets["VALID_USERNAME"]
github_token = st.secrets["GITHUB_TOKEN"]

# Listagens Page
if choice == "Ligar/Desligar":
    st.header("Ligar/Desligar")

    with st.form("Ligar/Desligar"):
        if not st.session_state.logged_in:
            username = st.text_input("Utilizador")
            password = st.text_input("Palavra passe", type="password")
            submitted = st.form_submit_button("Ligar")
            if submitted:
                if username == valid_username and bcrypt.checkpw(password.encode('utf-8'), valid_password):
                    st.session_state.logged_in = True
                    st.success(f"Bem vindo, {username}!. Já está ligado")
                else:
                    st.error("Utilizador ou senha incorretos.")                
        else:
            st.warning("Já está ligado. Para atualizar a base de dados, desligue-se.")
            submitted = st.form_submit_button("Desligar")
            if submitted:
                st.session_state.logged_in = False
                date = 'database updated at ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ghub.delete_from_github(github_token, "pbcachim/baralhos", "card_decks.db", date + '-del')
                ghub.upload_to_github(github_token, "pbcachim/baralhos", "card_decks.db", date)
                st.success(f"Desligado com sucesso!")

elif choice == "Listagens":
    st.header("Listagem de Baralhos de Cartas")

    if not st.session_state.logged_in:
        st.warning("Por favor faça login para aceder a esta página.")
        st.stop()

    types = cd.get_records("types")
    type_dict = dict(sorted({type_[1]: type_[0] for type_ in types}.items()))
    selected_type = st.selectbox("Filtrar por tipo de baralho", ["All"] + list(type_dict.keys()))

    numbers = cd.get_records("numbers")
    number_dict = dict(sorted({number[1]: number[0] for number in numbers}.items()))
    selected_number = st.selectbox("Filtrar por número de cartas", ["All"] + list(number_dict.keys()))

    themes = cd.get_records("themes")
    theme_dict = dict(sorted({theme[1]: theme[0] for theme in themes}.items()))
    selected_theme = st.selectbox("Filtrar por tema", ["All"] + list(theme_dict.keys()))

    games = cd.get_records("games")
    game_dict = dict(sorted({game[1]: game[0] for game in games}.items()))
    selected_game = st.selectbox("Filtrar por tipo de jogo", ["All"] + list(game_dict.keys()))

    cities = cd.get_records("cities")
    city_dict = dict(sorted({city[1]: city[0] for city in cities}.items()))
    selected_city = st.selectbox("Filtrar por cidade", ["All"] + list(city_dict.keys()))

    countries = cd.get_records("countries")
    country_dict = dict(sorted({country[1]: country[0] for country in countries}.items()))
    selected_country = st.selectbox("Filtrar por país", ["All"] + list(country_dict.keys()))

    collections = cd.get_records("collections")
    collection_dict = dict(sorted({collection[1]: collection[0] for collection in collections}.items()))
    selected_collection = st.selectbox("Filtrar por coleção", ["All"] + list(collection_dict.keys()))

    manufacturers = cd.get_records("manufacturers")
    manufacturer_dict = dict(sorted({manufacturer[1]: manufacturer[0] for manufacturer in manufacturers}.items()))
    selected_manufacturer = st.selectbox("Filtrar por fabricante", ["All"] + list(manufacturer_dict.keys()))

    # Apply Filters
    type_id = type_dict[selected_type] if selected_type != "All" else None
    number_id = number_dict[selected_number] if selected_number != "All" else None
    theme_id = theme_dict[selected_theme] if selected_theme != "All" else None
    game_id = game_dict[selected_game] if selected_game != "All" else None
    city_id = city_dict[selected_city] if selected_city != "All" else None
    country_id = country_dict[selected_country] if selected_country != "All" else None
    collection_id = collection_dict[selected_collection] if selected_collection != "All" else None
    manufacturer_id = manufacturer_dict[selected_manufacturer] if selected_manufacturer != "All" else None

    filtered_decks = cd.filter_decks(type_id, number_id, theme_id, game_id, city_id, country_id, collection_id, manufacturer_id)

    # Display all decks in a selectbox
    # deck_names = [f"{deck[0]}. {deck[1]}" for deck in filtered_decks]
    deck_names = cd.get_deck_names(filtered_decks)
    selected_deck_name = st.selectbox("Selecione um baralho para ver detalhes:", deck_names) # Added empty string for no selection

    if not filtered_decks:
        st.info("Não existem baralhos a apresentar com os filtros selecionados.")
    else:
        if selected_deck_name:  # Check if a deck is selected
            selected_deck_id = int(selected_deck_name.split(".")[0])
            selected_deck_details = cd.get_deck_by_id(selected_deck_id)

            if selected_deck_details:
                st.subheader(selected_deck_details[1])  # Display deck name as subheader
                st.write(f"Tipo: {selected_deck_details[1]}")
                st.write(f"Número de Cartas: {selected_deck_details[2]}")
                st.write(f"Tema: {selected_deck_details[3]}")
                st.write(f"Jogo: {selected_deck_details[4]}")
                st.write(f"Cidade: {selected_deck_details[5]}")
                st.write(f"País: {selected_deck_details[6]}")
                st.write(f"Coleção: {selected_deck_details[7]}")
                st.write(f"Fabricante: {selected_deck_details[8]}")
                st.write(f"Descrição: {selected_deck_details[9]}")

                image_data_list = selected_deck_details[10].split(",") if selected_deck_details[10] else []
                if image_data_list:
                    st.subheader("Imagens:")
                    for image_data in image_data_list:
                        try:
                            # Decode the base64 string
                            image_bytes = base64.b64decode(image_data)
                            # Use BytesIO to create an in-memory file-like object
                            image = Image.open(io.BytesIO(image_bytes))
                            # st.image(image, use_container_width=True)
                            st.image(image, width=200)
                        except Exception as e:
                            st.error(f"Erro ao exibir imagem: {e}")

                edit_button = st.button(f"Editar baralho", key=f"edit_button_{selected_deck_id}")
            else:
                st.error("Detalhes do baralho não encontrados.")

        # Export to Excel (Improved)
        df = pd.DataFrame(
            filtered_decks,
            columns=["ID", "Type", "Number of Cards", "Theme", "Game", "City", "Country", "Collection", "Manufacturer", "Description", "Images"]
        )
        df = df.drop(columns=["Images"])
        
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            # writer.close()

        excel_file = buffer.getvalue()

        st.download_button(
            label="Descarregar como Excel",
            data=excel_file,
            file_name="filtered_decks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        if edit_button:
            st.session_state.edit_deck_id = selected_deck_id
            st.session_state.choice_id = 3
        
# Adicionar Baralhos  Page
elif choice == "Adicionar Baralhos ":
    st.header("Adicionar Baralhos de Cartas")
    
    if not st.session_state.logged_in:
        st.warning("Por favor faça login para aceder a esta página.")
        st.stop()

    # Add Deck
    with st.form("add_deck_form"):
        types = cd.get_records("types")
        type_dict = dict(sorted({type_[1]: type_[0] for type_ in types}.items()))
        type_name = st.selectbox("Seleciona o tipo de baralho", list(type_dict.keys()))

        numbers = cd.get_records("numbers")
        number_dict = dict(sorted({number[1]: number[0] for number in numbers}.items()))
        number_name = st.selectbox("Seleciona o número de cartas do baralho", list(number_dict.keys()))

        themes = cd.get_records("themes")
        theme_dict = dict(sorted({theme[1]: theme[0] for theme in themes}.items()))
        theme_name = st.selectbox("Seleciona o tema", list(theme_dict.keys()))

        games = cd.get_records("games")
        game_dict = dict(sorted({game[1]: game[0] for game in games}.items()))
        game_name = st.selectbox("Seleciona o jogo", list(game_dict.keys()))

        cities = cd.get_records("cities")
        city_dict = dict(sorted({city[1]: city[0] for city in cities}.items()))
        city_name = st.selectbox("Seleciona a cidade", list(city_dict.keys()))

        countries = cd.get_records("countries")
        country_dict = dict(sorted({country[1]: country[0] for country in countries}.items()))
        country_name = st.selectbox("Seleciona o país", list(country_dict.keys()))

        collections = cd.get_records("collections")
        collection_dict = dict(sorted({collection[1]: collection[0] for collection in collections}.items()))
        collection_name = st.selectbox("Seleciona a coleção", list(collection_dict.keys()))

        manufacturers = cd.get_records("manufacturers")
        manufacturer_dict = dict(sorted({manufacturer[1]: manufacturer[0] for manufacturer in manufacturers}.items()))
        manufacturer_name = st.selectbox("Seleciona o fabricante", list(manufacturer_dict.keys()))

        description = st.text_area("Descrição")
        
        uploaded_files = st.file_uploader("Faça upload das imagens do baralho", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

        submitted = st.form_submit_button("Adicionar baralho")
        if submitted:
            image_paths = []
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    with open(uploaded_file.name, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                        image_paths.append(uploaded_file.name)
                        
            cd.add_deck(type_dict[type_name], number_dict[number_name], theme_dict[theme_name], game_dict[game_name], 
                        city_dict[city_name], country_dict[country_name], collection_dict[collection_name], 
                        manufacturer_dict[manufacturer_name], description, image_paths)
            st.success(f"Baralho adicionado com sucesso!")

    # View Decks
    st.subheader("Lista de baralhos")
    decks = cd.get_decks()
    for deck in decks:
        st.write(f"{deck[0]}. {deck[1]} - {deck[2]} cartas, Tema: {deck[3]}, Jogo: {deck[4]}, Cidade: {deck[5]}, País: {deck[6]}, Coleção: {deck[7]}, Fabricante: {deck[8]}, Descrição: {deck[9]}")

        # images_decoded = deck[5].split(",")
        # for img_data in images_decoded:
        #     st.image(base64.b64decode(img_data), use_container_width=True)

# Editar Baralhos  Page
elif choice == "Editar Baralhos ":
    st.header("Editar Baralhos de Cartas")
    
    if not st.session_state.logged_in:
        st.warning("Por favor faça login para aceder a esta página.")
        st.stop()

    # Edit Deck
    decks = cd.get_decks()
    # deck_names = [f"{deck[0]}. {deck[1]}" for deck in decks]
    deck_names = cd.get_deck_names(decks)
    selected_deck_name = st.selectbox("Selecione um baralho para editar:", deck_names, index=st.session_state.edit_deck_id)

    if selected_deck_name:
        selected_deck_id = int(selected_deck_name.split(".")[0])
        deck_details = cd.get_deck_by_id(selected_deck_id)

        if deck_details:
            with st.form(f"edit_deck_form_{selected_deck_id}"):
                types = cd.get_records("types")
                type_dict = dict(sorted({type_[1]: type_[0] for type_ in types}.items()))
                type_name = st.selectbox("Tipo de baralho", list(type_dict.keys()), index=list(type_dict.keys()).index(deck_details[1]))

                numbers = cd.get_records("numbers")
                number_dict = dict(sorted({number[1]: number[0] for number in numbers}.items()))
                number_name = st.selectbox("Número de cartas", list(number_dict.keys()), index=list(number_dict.keys()).index(str(deck_details[2])))

                themes = cd.get_records("themes")
                theme_dict = dict(sorted({theme[1]: theme[0] for theme in themes}.items()))
                theme_name = st.selectbox("Tema", list(theme_dict.keys()), index=list(theme_dict.keys()).index(deck_details[3]))

                games = cd.get_records("games")
                game_dict = dict(sorted({game[1]: game[0] for game in games}.items()))
                game_name = st.selectbox("Jogo", list(game_dict.keys()), index=list(game_dict.keys()).index(deck_details[4]))

                cities = cd.get_records("cities")
                city_dict = dict(sorted({city[1]: city[0] for city in cities}.items()))
                city_name = st.selectbox("Cidade", list(city_dict.keys()), index=list(city_dict.keys()).index(deck_details[5]))

                countries = cd.get_records("countries")
                country_dict = dict(sorted({country[1]: country[0] for country in countries}.items()))
                country_name = st.selectbox("País", list(country_dict.keys()), index=list(country_dict.keys()).index(deck_details[6]))

                collections = cd.get_records("collections")
                collection_dict = dict(sorted({collection[1]: collection[0] for collection in collections}.items()))
                collection_name = st.selectbox("Coleção", list(collection_dict.keys()), index=list(collection_dict.keys()).index(deck_details[7]))

                manufacturers = cd.get_records("manufacturers")
                manufacturer_dict = dict(sorted({manufacturer[1]: manufacturer[0] for manufacturer in manufacturers}.items()))
                manufacturer_name = st.selectbox("Fabricante", list(manufacturer_dict.keys()), index=list(manufacturer_dict.keys()).index(deck_details[8]))

                description = st.text_area("Descrição", value=deck_details[9])

                # Handle images for editing
                existing_images = deck_details[10].split(",") if deck_details[10] else []
                st.write("Imagens existentes:")
                for image_data in existing_images:
                    try:
                        image_bytes = base64.b64decode(image_data)
                        image = Image.open(io.BytesIO(image_bytes))
                        st.image(image, width=200)
                    except:
                        st.write("Erro a carregar imagem")

                uploaded_files = st.file_uploader("Adicionar/Substituir imagens", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

                submitted = st.form_submit_button("Guardar alterações")
                if submitted:
                    image_paths = existing_images
                    if uploaded_files:
                        image_paths = []
                        for uploaded_file in uploaded_files:
                            try:
                                image = Image.open(uploaded_file)
                                image_bytes = io.BytesIO()
                                image.save(image_bytes, format=image.format)
                                image_paths.append(image_bytes.getvalue())
                            except Exception as e:
                                st.error(f"Erro ao processar imagem: {e}")
                    cd.edit_deck(selected_deck_id, type_dict[type_name], number_dict[number_name], theme_dict[theme_name], game_dict[game_name],
                                city_dict[city_name], country_dict[country_name], collection_dict[collection_name],
                                manufacturer_dict[manufacturer_name], description, image_paths)
                    st.success("Baralho editado com sucesso!")
        else:
            st.error("Detalhes do baralho não encontrados.")

# Definições Page
elif choice == "Definições":
    st.header("Definições")

    if not st.session_state.logged_in:
        st.warning("Por favor faça login para aceder a esta página.")
        st.stop()

    tables = ["types", "themes", "games", "cities", "countries", "collections", "manufacturers", "numbers"]
    tables = tables_list.keys()
    table_choice_pt = st.selectbox("Seleciona a tabela a modificar", tables)
    table_choice = tables_list[table_choice_pt]

    # Add Record
    with st.form(f"add_{table_choice}_form"):
        # record_name = st.text_input(f"{table_choice[:-1].capitalize()} Name")
        record_name = st.text_input(tables_choice[table_choice_pt])
        submitted = st.form_submit_button("Adicionar")
        if submitted and record_name:
            if cd.add_record(table_choice, record_name):
                st.success(f"Record '{record_name}' added successfully!")
            else:
                st.warning(f"Record '{record_name}' already exists or there was an error.") # More user-friendly message

    # View and Delete Records
    records = cd.get_records(table_choice)
    for record in records:
        st.write(f"{record[0]}. {record[1]}")
        if st.button(f"Eliminar {record[1]}", key=f"delete_{table_choice}_{record[0]}"):
            cd.delete_record(table_choice, record[0])
            st.success(f"{tables_choice[table_choice_pt]} '{record[1]}' eliminado com sucesso!")
