from flask import Flask, render_template, send_file, abort, request
import sqlite3
from io import BytesIO
from flask_caching import Cache
from flask import jsonify

app = Flask(__name__, template_folder='templates', static_folder='static')


db_path = './database.db'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/acoustic', methods=['GET', 'POST'])
def acoustic_page():
    search_query = request.form.get('search', '')

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        if search_query:
            query = '''
            SELECT file_name, note, fundamental_frequency, theoretical_frequency, mean_deviation_percent, fft_plot, comparison_plot
            FROM FrequencyData
            WHERE (file_name LIKE ? OR note LIKE ?) AND type = 'acoustic'
            '''
            params = (f'%{search_query}%', f'%{search_query}%')
            cursor.execute(query, params)
        else:
            cursor.execute('''
            SELECT file_name, note, fundamental_frequency, theoretical_frequency, mean_deviation_percent, fft_plot, comparison_plot
            FROM FrequencyData
            WHERE type = 'acoustic'
            ''')
        data = cursor.fetchall()
    except Exception as e:
        print(f"Error while calling the data for the acoustic guitar: {e}")
        data = []
    finally:
        connection.close()

    return render_template('index.html', data=data, guitar_type='Acoustic')

@app.route('/western', methods=['GET', 'POST'])
def western_page():
    search_query = request.form.get('search', '')

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        if search_query:
            query = '''
            SELECT file_name, note, fundamental_frequency, theoretical_frequency, mean_deviation_percent, fft_plot, comparison_plot
            FROM FrequencyData
            WHERE (file_name LIKE ? OR note LIKE ?) AND type = 'western'
            '''
            params = (f'%{search_query}%', f'%{search_query}%')
            cursor.execute(query, params)
        else:
            cursor.execute('''
            SELECT file_name, note, fundamental_frequency, theoretical_frequency, mean_deviation_percent, fft_plot, comparison_plot
            FROM FrequencyData
            WHERE type = 'western'
            ''')
        data = cursor.fetchall()
    except Exception as e:
        print(f"Error while calling the data for the western guitar: {e}")
        data = []
    finally:
        connection.close()

    return render_template('index.html', data=data, guitar_type='Western')

@app.route('/plot/<file_name>/fft')
def get_fft_plot(file_name):
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute('SELECT fft_plot FROM FrequencyData WHERE file_name = ?', (file_name,))
        result = cursor.fetchone()
    except Exception as e:
        print(f"Error while calling the Diagram: {e}")
        result = None
    finally:
        connection.close()

    if result and result[0]:
        return send_file(BytesIO(result[0]), mimetype='image/png')
    else:
        abort(404, description="Diagram not found.")

@app.route('/plot/<file_name>/comparison')
def get_comparison_plot(file_name):
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute('SELECT comparison_plot FROM FrequencyData WHERE file_name = ?', (file_name,))
        result = cursor.fetchone()
    except Exception as e:
        print(f"Error while calling the reference diagram: {e}")
        result = None
    finally:
        connection.close()

    if result and result[0]:
        return send_file(BytesIO(result[0]), mimetype='image/png')
    else:
        abort(404, description="Comparison Diagram was not found.")


@app.route('/synthesizer')
def synthesizer():
    return render_template('synthesizer.html')

@app.route('/api/frequencies')
def get_frequencies():
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT DISTINCT note, fundamental_frequency FROM FrequencyData WHERE type='acoustic'")
        acoustic_frequencies = {row[0]: row[1] for row in cursor.fetchall()}  

        cursor.execute("SELECT DISTINCT note, fundamental_frequency FROM FrequencyData WHERE type='western'")
        western_frequencies = {row[0]: row[1] for row in cursor.fetchall()}  

    except Exception as e:
        print(f"Error while loading the frequencies: {e}")
        return jsonify({"acoustic": [], "western": []}), 500
    finally:
        connection.close()

    return jsonify({
        "acoustic": [{"note": note, "frequency": freq} for note, freq in acoustic_frequencies.items()],
        "western": [{"note": note, "frequency": freq} for note, freq in western_frequencies.items()]
    })

@app.route('/api/measurements')
def get_measurements():
    guitar_type = request.args.get('type', 'acoustic')
    all_types = request.args.get('all_types', 'false').lower() == 'true'
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        if all_types:
            cursor.execute("SELECT file_name, note, type FROM FrequencyData")
            rows = cursor.fetchall()
            measurements = [
                {"file_name": row[0], "note": row[1], "type": row[2]}
                for row in rows
            ]
        else:
            cursor.execute("SELECT file_name, note FROM FrequencyData WHERE type = ?", (guitar_type,))
            rows = cursor.fetchall()
            measurements = [
                {"file_name": row[0], "note": row[1]}
                for row in rows
            ]
    except Exception as e:
        print(f"Error while loading measurements: {e}")
        return jsonify([]), 500
    finally:
        connection.close()
    return jsonify(measurements)

if __name__ == '__main__':
    app.run(debug=True)
