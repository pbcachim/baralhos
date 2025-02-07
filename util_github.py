from github import Github
from github.GithubException import UnknownObjectException, GithubException
import os

# Upload/download to/from GitHub
def upload_binary_to_github(token, repo_name, file_path, commit_message, branch="main"):
    """Uploads a binary file to a GitHub repository.

    Args:
        token (str): Personal access token from GitHub.
        repo_name (str): Name of the GitHub repository (owner/repo).
        file_path (str): Full path to the binary file you want to upload.
        commit_message (str): Commit message for the upload.
        branch (str, optional): The branch to commit to. Defaults to "main".

    Returns:
        bool: True on successful upload, False otherwise.
    Raises:
        FileNotFoundError: If the specified file is not found.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        g = Github(token)
        repo = g.get_repo(repo_name)

        with open(file_path, "rb") as file:
            content = file.read()

        file_name = os.path.basename(file_path)

        # Determine content type based on file extension (optional)
        content_type = None
        # Example using mimetypes library (install with pip install mimetypes)
        # import mimetypes
        # content_type = mimetypes.guess_type(file_path)[0]

        repo.create_file(file_name, commit_message, content, branch=branch, content_type=content_type)
        print(f"Successfully uploaded '{file_path}' to '{repo_name}' on branch '{branch}'")
        return True

    except UnknownObjectException as e:
        print(f"Repository not found or you don't have access: {e}")
        return False
    except GithubException as e:
        print(f"A GitHub error occurred: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def download_binary_from_github(token, repo_name, file_path, branch="main"):
    """Downloads a binary file from a GitHub repository.

    Args:
        token (str): Personal access token from GitHub.
        repo_name (str): Name of the GitHub repository (owner/repo).
        file_path (str): Path to the file in the repository.
        branch (str, optional): The branch to download from. Defaults to "main".

    Returns:
        bool: True on successful download, False otherwise.
    """
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)

        try:
            contents = repo.get_contents(file_path, ref=branch)
        except UnknownObjectException:
            print(f"File '{file_path}' not found in repository '{repo_name}' on branch '{branch}'.")
            return False

        if contents.encoding is not None and contents.encoding == 'base64':
            import base64
            decoded = base64.b64decode(contents.content)
            with open(os.path.basename(file_path), 'wb') as f:
                f.write(decoded)
        else:
            with open(os.path.basename(file_path), 'wb') as f:
                f.write(contents.decoded_content)

        print(f"Successfully downloaded '{file_path}' from '{repo_name}' on branch '{branch}'.")
        return True

    except UnknownObjectException as e:
        print(f"Repository '{repo_name}' not found or you don't have access: {e}")
        return False
    except GithubException as e:
        print(f"A GitHub error occurred: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def upload_to_github(token, repo_name, file_path, commit_message, branch='main'):
    """Uploads a file to a GitHub repository.

    Args:
        token (str): Personal access token from GitHub.
        repo_name (str): Name of the GitHub repository (owner/repo).
        file_path (str): Full path to the file you want to upload.
        commit_message (str): Commit message for the upload.
        branch (str): Name of the branch where the file is located (default: 'main').

    Returns:
        bool: True on successful upload, False otherwise.

    Raises:
        FileNotFoundError: If the specified file is not found.
        GithubException: If there's an error interacting with the GitHub API.
    """

    # Validate file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    g = Github(token)  # Create GitHub object
    repo = g.get_repo(repo_name)  # Get the repository

    try:
        # Read the file content in binary mode
        with open(file_path, 'rb') as file:
            content = file.read()

        # Create the file in the specified branch (default: main)
        repo.create_file(os.path.basename(file_path), commit_message, content, branch=branch)
        print(f"Successfully uploaded {file_path} to {repo_name}")
        return True

    except UnknownObjectException as e:
        print(f"Repository not found or you don't have access: {e}")
        return False
    except GithubException as e:  # Catch other GitHub-related errors
        print(f"A GitHub error occurred: {e}")
        return False
    except Exception as e: # Catch other exception
        print(f"An unexpected error occurred: {e}")
        return False

def delete_from_github(token, repo_name, file_path, commit_message, branch='main'):
    """Deleta um arquivo de um repositório no GitHub.

    Args:
        token (str): Token de acesso pessoal do GitHub.
        repo_name (str): Nome do repositório no GitHub (owner/repo).
        file_path (str): Caminho do arquivo que você deseja deletar (relativo à raiz do repositório).
        commit_message (str): Mensagem do commit para a deleção.
        branch (str): Nome do branch onde o arquivo está localizado (default: 'main').

    Returns:
        bool: True em caso de sucesso, False caso contrário.
    """
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)

        try:
            file = repo.get_contents(file_path, ref=branch)
        except UnknownObjectException:
            print(f"Arquivo '{file_path}' não encontrado no repositório.")
            return False

        repo.delete_file(
            path=file.path,
            message=commit_message,
            sha=file.sha,
            branch=branch,
        )
        print(f"Arquivo '{file_path}' deletado com sucesso do repositório '{repo_name}'.")
        return True

    except UnknownObjectException as e:
        print(f"Repositório '{repo_name}' não encontrado ou você não tem acesso: {e}")
        return False
    except GithubException as e:
        print(f"Um erro do GitHub ocorreu: {e}")
        return False
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}")
        return False

# Example usage
if __name__ == '__main__':
    your_token = "YOUR_PERSONAL_ACCESS_TOKEN"  # Replace with your token
    repo_name = "your_username/your_repo"  # Replace with your repo
    file_path = "path/to/your/binary_file.dat"  # Replace with the file path
    branch_name = "develop" # Replace for your branch

    success = download_binary_from_github(your_token, repo_name, file_path, branch_name)
    if success:
        print("Download completed!")
    else:
        print("Download failed.")

    success = download_binary_from_github(your_token, repo_name, file_path) # Uses default branch "main"
    if success:
        print("Download completed!")
    else:
        print("Download failed.")