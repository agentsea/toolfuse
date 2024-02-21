import subprocess

def main():
    subprocess.run([
        'sphinx-build',
        '-b', 'html',
        'docs/',
        'docs/_build/html'
    ])

if __name__ == "__main__":
    main()