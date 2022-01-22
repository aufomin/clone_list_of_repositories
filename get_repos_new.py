from msa_services import list_of_repositories
from git import Repo, Git
import os.path
import glob
import fileinput

# ssh://{bitbucket_hostname}:{port}/{project_name}
base_url = r"ssh://git@bitbucket.com:9999/msa"

# Where to create folder to clone repositories
base_dir = f"{os.getcwd()}/repositories"

# Branch to be created
branch_name = "MSA-3928/add-labeling"

# Which file needs to be changed
file_for_changing = "deployment.yaml"

string_to_insert = "        deployment: {{ .Values.serviceName }}-{{ .Values.color }}\n"
commit_msg = "[ABC-3928] add new label"
root_dir = os.getcwd()
# Under which line should a new line be inserted?
adjacent_line = "labels:"


def clone_msa_microservices(services):
    for service in services:
        repository_dir = f"{base_dir}/{service}"
        if not os.path.exists(repository_dir):
            os.makedirs(repository_dir)
            Git(base_dir).clone(f"{base_url}/{service}.git")
            print(f"{service} successfully cloned")
            required_file = find_required_file(repository_dir)
            if not check_if_the_string_is_exist(required_file, string_to_insert):
                checkout(repository_dir)
                add_new_string_to_the_required_file(required_file)
                commit_and_push(repository_dir, required_file)
            os.chdir(root_dir)
        else:
            print(f"{service} already cloned")
            checkout(repository_dir)
            required_file = find_required_file(repository_dir)
            if not check_if_the_string_is_exist(required_file, string_to_insert):
                checkout(repository_dir)
                add_new_string_to_the_required_file(required_file)
                commit_and_push(repository_dir, required_file)
            os.chdir(root_dir)


def checkout(repository_dir):
    repo = Repo(repository_dir)
    os.chdir(repository_dir)
    try:
        repo.git.checkout(b=branch_name)
    except:
        repo.git.checkout(branch_name)


def commit_and_push(repository_dir, file):
    repo = Repo(repository_dir)
    repo.index.add(file)
    repo.index.commit(commit_msg)
    origin = repo.remote()
    repo.create_head(branch_name)
    origin.push(branch_name)


def find_required_file(directory):
    pathname = directory + f"/**/{file_for_changing}"
    print(pathname)
    return glob.glob(pathname, recursive=True)


def check_if_the_string_is_exist(file, string):
    file = string.join(file)
    print(f"check_if_the_string_is_exist: {file}")
    try:
        with open(file) as f:
            if string in f.read():
                print(f"String {string} already exists".replace("\n", ""))
                return True
            else:
                print(f"{string} doesn't exist. {string} will be added to the {file}".replace("\n", ""))
                return False
    except:
        print(f"The required file does not exist and should not contain this {string}")
    return True


def add_new_string_to_the_required_file(file):
    for line in fileinput.FileInput(file, inplace=1):
        if adjacent_line in line:
            line = line.replace(line, line + string_to_insert)
        print(line, end='')


clone_msa_microservices(list_of_repositories)
