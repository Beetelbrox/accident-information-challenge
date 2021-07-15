import zipfile
import os

def download_kaggle_file_with_credentials(
        dataset: str, 
        file: str,
        kaggle_api_username: str,
        kaggle_api_key: str,
        download_path: str,
        force: bool=False,
        quiet: bool=False,
        unzip: bool=True
    ) -> None:
    # Check the existence of files if we are unzipping but not forcing download as dataset_download_file only check the
    # existence of the compressed file. Otherwise delegate to dataset_download_file.
    if not force and unzip:
        if os.path.isfile(f'{download_path}/{file}'):
            print(f'Download Kaggle File: File {file} already exists at the download location. Skipping download')
            return
    # Inject environment variables with the kaggle authentication in order to be able to authenticate.
    os.environ['KAGGLE_USERNAME'] = kaggle_api_username
    os.environ['KAGGLE_KEY'] = kaggle_api_key
    download_kaggle_file(dataset, file, download_path, force, quiet)
    # Unzip the file if necessary
    if unzip:
        zipped_file_path = f'{download_path}/{file}.zip'
        with zipfile.ZipFile(zipped_file_path, 'r') as zipped_file:
            zipped_file.extractall(download_path)
        os.remove(zipped_file_path)

def download_kaggle_file(dataset: str, file: str, download_path: str, force: bool, quiet: bool) -> None:
    # We need to import the Kaggle api here because for some reason it tries to authenticate as soon as you import the
    # package (https://github.com/Kaggle/kaggle-api/blob/master/kaggle/__init__.py) and can crash airflow on startup
    import kaggle
    kaggle.api.dataset_download_file(dataset, file, download_path, force, quiet)