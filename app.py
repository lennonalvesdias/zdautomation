import traceback
from flask import Flask, request, jsonify
import pandas as pd
from macros_service import MacroService
from api.zendesk import Client as ZenClient
from dotenv import dotenv_values

app = Flask(__name__)
config = dotenv_values(".env")


@app.route("/")
def hello_world():
    return {
        'message': 'Hello world!'
    }


@app.route('/uploads/macros', methods=['POST'])
def csv_upload():
    filebuf = request.files.get('file')

    if filebuf is None:
        return jsonify(message='Nenhum arquivo encontrado.'), 400
    elif 'text/csv' != filebuf.mimetype:
        return jsonify(message='Extensão de arquivo inválida.'), 415

    data = pd.read_csv(filebuf, sep=';', encoding='utf8')
    data = data.fillna('')
    # app.logger.debug(data.info())

    errors = []
    macros = []

    client = ZenClient(config['ZD_INSTANCE'], config['ZD_EMAIL'], config['ZD_TOKEN'])
    macro_service = MacroService(client)

    for index, row in data.iterrows():
        try:
            # app.logger.info(f'Process macro {row.title}')
            update = request.form.get('update', '').lower() == 'true'
            macro = macro_service.proccess_row(row, update)
            macros.append(macro)
        except Exception as err:
            errors.append(f'Error in macro [{index}] {row[0]} >> {err}')
            app.logger.error(traceback.format_exc())

    return jsonify(
        message=f'Arquivo {filebuf.filename!r} encontrado. {len(macros)} linha(s) com sucesso e {len(errors)} com erro(s).',
        macros=macros,
        errors=errors), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
