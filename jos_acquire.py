"""
A module for obtaining repo readme and language data from the github API.
Before using this module, read through it, and follow the instructions marked
TODO.
After doing so, run it like this:
    python acquire.py
To create the `data.json` file that contains the data.
"""
import os
import json
from typing import Dict, List, Optional, Union, cast
import requests

from env import github_token, github_username

# TODO: Make a github personal access token.
#     1. Go here and generate a personal access token https://github.com/settings/tokens
#        You do _not_ need select any scopes, i.e. leave all the checkboxes unchecked
#     2. Save it in your env.py file under the variable `github_token`
# TODO: Add your github username to your env.py file under the variable `github_username`
# TODO: Add more repositories to the `REPOS` list below.

REPOS = [
    ['/apple/llvm-project',
     '/apple/swift',
     '/apple/sourcekit-lsp',
     '/apple/foundationdb',
     '/apple/swift-docc',
     '/apple/swift-protobuf',
     '/apple/swift-llbuild',
     '/apple/swift-syntax',
     '/apple/swift-package-manager',
     '/apple/swift-source-compat-suite',
     '/apple/swift-markdown',
     '/apple/swift-docc-symbolkit',
     '/apple/swift-docc-render-artifact',
     '/apple/swift-lmdb',
     '/apple/swift-tools-support-core',
     '/apple/swift-driver',
     '/apple/indexstore-db',
     '/apple/swift-stress-tester',
     '/apple/swift-xcode-playground-support',
     '/apple/swift-integration-tests',
     '/apple/swift-cmark',
     '/apple/swift-corelibs-libdispatch',
     '/apple/swift-corelibs-foundation',
     '/apple/swift-corelibs-xctest',
     '/apple/swift-experimental-string-processing',
     '/apple/swift-docker',
     '/apple/swift-installer-scripts',
     '/apple/swift-llbuild2',
     '/apple/swift-docc-render',
     '/apple/swift-evolution',
     '/apple/servicetalk',
     '/apple/swift-nio-ssh',
     '/apple/password-manager-resources',
     '/apple/swift-nio',
     '/apple/ml-hypersim',
     '/apple/swift-collections',
     '/apple/coremltools',
     '/apple/swift-atomics',
     '/apple/swift-log',
     '/apple/swift-distributed-actors',
     '/apple/swift-algorithms',
     '/apple/swift-argument-parser',
     '/apple/apple-llvm-infrastructure-tools',
     '/apple/swift-collections-benchmark',
     '/apple/cloudkit-sample-sharing',
     '/apple/cloudkit-sample-queries',
     '/apple/cloudkit-sample-privatedb-sync',
     '/apple/cloudkit-sample-privatedb',
     '/apple/cloudkit-sample-encryption',
     '/apple/cloudkit-sample-coredatasync',
     '/apple/example-package-playingcard',
     '/apple/swift-distributed-tracing',
     '/apple/swift-distributed-tracing-baggage',
     '/apple/swift-nio-ssl',
     '/apple/swift-tools-support-async',
     '/apple/swift-package-collection-generator',
     '/apple/swift-crypto',
     '/apple/swift-docc-plugin',
     '/apple/ARKitScenes',
     '/apple/swift-metrics',
     '/apple/swift-metrics-extras',
     '/apple/swift-nio-http2',
     '/apple/swift-http-structured-headers',
     '/apple/swift-nio-extras',
     '/apple/swift-nio-transport-services',
     '/apple/darwin-xnu',
     '/apple/swift-system',
     '/apple/swift-format',
     '/apple/ml-cvnets',
     '/apple/ml-knowledge-conflicts',
     '/apple/swift-sample-distributed-actors-transport',
     '/apple/swift-numerics',
     '/apple/cups',
     '/apple/swift-package-registry-compatibility-test-suite',
     '/apple/swift-se0288-is-power',
     '/apple/swift-standard-library-preview',
     '/apple/swift-se0270-range-set',
     '/apple/ml-core',
     '/apple/FHIRModels',
     '/apple/turicreate',
     '/apple/swift-service-discovery',
     '/apple/HomeKitADK',
     '/apple/GCGC',
     '/apple/swift-community-hosted-continuous-integration',
     '/apple/tensorflow_macos',
     '/apple/swift-nio-examples',
     '/apple/learning-compressible-subspaces',
     '/apple/ccs-pykerberos',
     '/apple/swift-internals',
     '/apple/example-package-fisheryates',
     '/apple/ml-shuffling-amplification',
     '/apple/ml-gsn',
     '/apple/ccs-caldavtester',
     '/apple/swift-evolution-staging',
     '/apple/example-package-dealer',
     '/apple/ml-cvpr2019-swd',
     '/apple/example-package-deckofplayingcards',
     '/apple/ml-covid-mobility',
     '/apple/swift-statsd-client',
     '/apple/AudioUnitSDK',
     '/apple/swift-nio-zlib-support',
     '/apple/openjdk',
     '/apple/ml-uwac',
     '/apple/darwin-libpthread',
     '/apple/ml-probabilistic-attention',
     '/apple/ml-envmapnet',
     '/apple/ml-cread',
     '/apple/swift-distributed-tracing-baggage-core',
     '/apple/ml-stuttering-events-dataset',
     '/apple/ml-multiple-futures-prediction',
     '/apple/ml-qrecc',
     '/apple/apple_rules_lint',
     '/apple/vqg-multimodal-assistant',
     '/apple/ccs-pycalendar',
     '/apple/learning-subspaces',
     '/apple/darwin-libplatform',
     '/apple/ml-quant',
     '/apple/ml-equivariant-neural-rendering',
     '/apple/swift-nio-nghttp2-support',
     '/apple/swift-nio-ssl-support',
     '/apple/swift-cluster-membership',
     '/apple/ml-tree-dst',
     '/apple/ml-collegial-ensembles',
     '/apple/swiftpm-on-llbuild2',
     '/apple/ml-transcript-translation-consistency-ratings',
     '/apple/ml-mkqa',
     '/apple/ml-dab',
     '/apple/ml-capsules-inverted-attention-routing',
     '/apple/ccs-calendarserver',
     '/apple/swift-lldb',
     '/apple/ml-cifar-10-faster',
     '/apple/ml-data-parameters',
     '/apple/ml-afv',
     '/apple/swift-llvm',
     '/apple/swift-clang',
     '/apple/swift-clang-tools-extra',
     '/apple/swift-libcxx',
     '/apple/swift-compiler-rt',
     '/apple/llvm-project-v5-split',
     '/apple/llvm-project-v5',
     '/apple/llvm-monorepo-root',
     '/apple/ml-ncg',
     '/apple/ccs-twistedextensions',
     '/apple/ml-all-pairs',
     '/apple/swift-3-api-guidelines-review',
     '/apple/ccs-pyopendirectory',
     '/apple/swift-protobuf-plugin',
     '/apple/ccs-caldavclientlibrary',
     '/apple/ccs-pyosxframeworks',
     '/apple/ccs-pysecuretransport',
     '/apple/swift-protobuf-test-conformance']
]

headers = {"Authorization": f"token {github_token}",
           "User-Agent": github_username}

if headers["Authorization"] == "token " or headers["User-Agent"] == "":
    raise Exception(
        "You need to follow the instructions marked TODO in this script before trying to use it"
    )


def github_api_request(url: str) -> Union[List, Dict]:
    response = requests.get(url, headers=headers)
    response_data = response.json()
    if response.status_code != 200:
        raise Exception(
            f"Error response from github api! status code: {response.status_code}, "
            f"response: {json.dumps(response_data)}"
        )
    return response_data


def get_repo_language(repo: str) -> str:
    url = f"https://api.github.com/repos/{repo}"
    repo_info = github_api_request(url)
    if type(repo_info) is dict:
        repo_info = cast(Dict, repo_info)
        if "language" not in repo_info:
            raise Exception(
                "'language' key not round in response\n{}".format(
                    json.dumps(repo_info))
            )
        return repo_info["language"]
    raise Exception(
        f"Expecting a dictionary response from {url}, instead got {json.dumps(repo_info)}"
    )


def get_repo_contents(repo: str) -> List[Dict[str, str]]:
    url = f"https://api.github.com/repos/{repo}/contents/"
    contents = github_api_request(url)
    if type(contents) is list:
        contents = cast(List, contents)
        return contents
    raise Exception(
        f"Expecting a list response from {url}, instead got {json.dumps(contents)}"
    )


def get_readme_download_url(files: List[Dict[str, str]]) -> str:
    """
    Takes in a response from the github api that lists the files in a repo and
    returns the url that can be used to download the repo's README file.
    """
    for file in files:
        if file["name"].lower().startswith("readme"):
            return file["download_url"]
    return ""


def process_repo(repo: str) -> Dict[str, str]:
    """
    Takes a repo name like "gocodeup/codeup-setup-script" and returns a
    dictionary with the language of the repo and the readme contents.
    """
    contents = get_repo_contents(repo)
    readme_download_url = get_readme_download_url(contents)
    if readme_download_url == "":
        readme_contents = ""
    else:
        readme_contents = requests.get(readme_download_url).text
    return {
        "repo": repo,
        "language": get_repo_language(repo),
        "readme_contents": readme_contents,
    }


def scrape_github_data() -> List[Dict[str, str]]:
    """
    Loop through all of the repos and process them. Returns the processed data.
    """
    return [process_repo(repo) for repo in REPOS]


if __name__ == "__main__":
    data = scrape_github_data()
    json.dump(data, open("data.json", "w"), indent=1)