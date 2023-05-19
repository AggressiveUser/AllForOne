#!/usr/bin/env python3

import os
import subprocess
import shutil
import time
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, wait
# SCRIPT BY AGGRESSIVEUSER
# GITHUB: https://github.com/Aggressiveuser
# Linkedin: https://www.linkedin.com/in/AggressiveUser/
# Twitter: https://twitter.com/AggressiveUserX
# HackTheBox: https://app.hackthebox.com/profile/17569
print("\033[91m\033[93m  ,-.       _,---._ __  / \      _   _ _     ___              ___               ")
print(r" /  )    .-'       `./ /   \    /_\ | | |   / __\__  _ __    /___\_ __   ___    ")
print(r"(  (   ,'            `/    /|  //_\\| | |  / _\/ _ \| '__|  //  // '_ \ / _ \   ")
print(r' \  `-"             \ \   / | /  _  \ | | / / | (_) | |    / \_//| | | |  __/   ')
print(r"  `.              ,  \ \ /  | \_/ \_/_|_| \/   \___/|_|    \___/ |_| |_|\___|   ")
print(r"   /`.          ,'-`----Y   |              					")
print(r"  (            ;        |   '        				                ")
print(r"  |  ,-.    ,-' Git-HUB |  /         Nuclei Template Collector                  ")
print(r"  |  | (   |      BoX   | /	          - AggressiveUser                      ")
print(r"  )  |  \  `.___________|/                                   			")
print("  `--'   `--'                                               			\033[0m")

def git_clone(url, destination):
    env = os.environ.copy()
    env['GIT_TERMINAL_PROMPT'] = '0'
    result = subprocess.run(['git', 'clone', url, destination], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=env)
    return result.returncode, result.stderr.decode().strip()

def generate_destination_folder(url):
    folder_name = os.path.basename(url.rstrip('.git'))
    counter = 1
    while os.path.exists(os.path.join('TRASH', folder_name)):
        folder_name = f"{os.path.basename(url.rstrip('.git'))}_{counter}"
        counter += 1
    return folder_name

def clone_repository(repo):
    destination = generate_destination_folder(repo)
    return_code, error_msg = git_clone(repo, os.path.join('TRASH', destination))
    if return_code != 0 or 'Username for' in error_msg:
        return repo
    return None

def clone_repositories(file_url):
    response = requests.get(file_url)
    if response.status_code == 200:
        repositories = response.text.strip().split('\n')
    else:
        print('Failed to retrieve Repo List from the server.')
        return

    total_repos = len(repositories)

    os.makedirs('TRASH', exist_ok=True) 

    failed_repos = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(clone_repository, repo) for repo in repositories]

        with tqdm(total=total_repos, unit='repo', desc='Cloning repositories', ncols=80) as progress_bar:
            completed = 0
            while completed < total_repos:
                done, _ = wait(futures, return_when='FIRST_COMPLETED')
                completed += len(done)
                for future in done:
                    failed_repo = future.result()
                    if failed_repo:
                        failed_repos.append(failed_repo)
                    progress_bar.update(1)
                    progress = progress_bar.n / total_repos * 100
                    progress_bar.set_postfix({'Progress': f'{progress:.2f}%'})
                futures = [future for future in futures if not future.done()]

    print('Cloning process complete!\n')

    if failed_repos:
        print("\033[91mFailed to clone the following repositories:\033[0m")
        for repo in failed_repos:
            print(repo)

    template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Template')
    if not os.path.exists(template_folder):
        os.makedirs(template_folder)

    yaml_count = 0
    for root, dirs, files in os.walk('TRASH'):
        for file in files:
            if file.endswith('.yaml'):
                source_path = os.path.join(root, file)
                destination_path = os.path.join(template_folder, file)
                shutil.copy2(source_path, destination_path)
                yaml_count += 1

    print(f'\033[92m \n{yaml_count} Nuclei Templates files copied to the Template folder.\033[0m')
    
    shutil.rmtree('TRASH')
    print('\nRemoving caches and temporary files.\n')
    time.sleep(2)
    print('\033[91m\033[93mPlease show your support by giving star to my GitHub repository "AllForOne".')
    print('GITHUB: https://github.com/AggressiveUser/AllForOne\033[0m')
    
file_url = 'https://raw.githubusercontent.com/AggressiveUser/AggressiveUser.github.io/main/PleaseUpdateMe.txt'

clone_repositories(file_url)
