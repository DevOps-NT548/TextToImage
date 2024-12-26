### Instruction

0. Put the private files into Backend/ folder (.env and .json files)

1. Create a new virtual environment with Python and activate it.

```
cd Backend/
python -m venv env
source env/bin/activate
```

**Suggestion**: Using `conda` with `python=3.11` if you don't want to use Python venv.
```
conda create -n backend python=3.11
conda activate backend
```

2. Install the dependencies.

```
pip install -r requirements.txt
```

3. Run the application (make sure you have PostgreSQL running on your machine and please change the database settings in settings.py to your own database settings...)

- If you have `bash/zsh/sh/...` shells, just replace with the `<shell>` that you have. For example, you have `bash`:
    ```
    bash setup.sh
    ```