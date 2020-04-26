from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, flash
from bson import json_util
from bson.objectid import ObjectId
from db import connect_db, initialize
import os 


app = Flask(__name__)

"""Declarar directorio de subida de imagenes"""
app.config['IMG_FOLDER'] = './static/img'

"""Clave necesaria para poder utilizar flash"""
app.secret_key = 'clave_secreta'

#Conexion a la bd
db = connect_db()

#Borrar coleccion
#db.heroes.drop()

#Checkear que haya datos en la bd
collist = db.list_collection_names()
if "heroes" not in collist:
    #cargar datos
    initialize(db) 


@app.route('/', methods=['GET'])
def get_heroes():
    #Obtener heroes de ambas casas
    data = db.heroes.find().sort('name')
    #Convertir BSON a JSON
    data = json_util.dumps(data)
    #json list
    data = json_util.loads(data)
    return render_template('home.html', data=data)  

@app.route('/marvel', methods=['GET'])
def get_heroes_marvel():
    #Obtener heroes de marvel
    data = db.heroes.find({"house": "MARVEL"}).sort('name')
    data = json_util.dumps(data)
    data = json_util.loads(data)
    return render_template('home.html', data=data)  

@app.route('/dc', methods=['GET'])
def get_heroes_dc():
    #Obtener heroes de dc
    data = db.heroes.find({"house": "DC"}).sort('name')
    data = json_util.dumps(data)
    data = json_util.loads(data)
    return render_template('home.html', data=data)  

@app.route('/add-hero', methods=['POST', 'GET'])
def add_hero():
    if request.method == 'GET':
        return render_template('add.html')
    else:
        #Recibiendo datos
        name = request.form.get('name')
        character = request.form.get('character')
        year = request.form.get('year')
        house = request.form.get('house')
        biography = request.form.get('biography')
        equipment = request.form.get('equipment')
        images = []
        
        # Guardar cada imagen en el servidor
        for file in request.files.getlist('images'):
            #Almacenar el nombre del archivo
            images.append(file.filename)
            file.save(os.path.join(app.config['IMG_FOLDER'], file.filename))   
                       
        if name and year and biography and house and images:
            
            if (character == None or character == '') and (equipment == None or equipment == ''):
                hero = {
                        "name": name,
                        "year": year,
                        "house": house,
                        "biography": biography,
                        "images": images,
                        "limit_images": len(images)
                    }
            elif (character == None or character == ''):
                hero = {
                        "name": name,
                        "year": year,
                        "house": house,
                        "biography": biography,
                        "equipment": equipment,
                        "images": images,
                        "limit_images": len(images)
                    }
            elif (equipment == None or equipment == ''):
                hero = {
                        "name": name,
                        "character": character,
                        "year": year,
                        "house": house,
                        "biography": biography,
                        "images": images,
                        "limit_images": len(images)
                    }
            else:
                hero = {
                        "name": name,
                        "character": character,
                        "year": year,
                        "house": house,
                        "biography": biography,
                        "equipment": equipment,
                        "images": images,
                        "limit_images": len(images)
                    }
            #Insertar objeto
            try:
                db.heroes.insert_one(hero)
                flash('Hero added successfully!')
                return redirect(url_for('get_heroes'))
            except Exception as err:
                print("An exception occurred :", err)
                flash('An error has occurred...')
                redirect('/add-hero')


@app.route('/delete/<id>', methods=['GET'])
def delete_hero(id):
    #Transformar el id (string) a un objectId
    try:
        db.heroes.delete_one({'_id': ObjectId(id)})
        flash('Hero deleted successfully!')
        return redirect(url_for('get_heroes'))
    except Exception as err:
        print("An exception occurred :", err)
        flash('An error has occurred...')
        return redirect('/hero/' + id)

@app.route('/update/<id>', methods=['GET', 'POST'])
def update_hero(id):
    #Obtener house e imagenes
    data = db.heroes.find_one({'_id': ObjectId(id)}, {'house': 1, 'images': 2, '_id': 0})
    #Recibiendo datos
    name = request.form.get('name')
    character = request.form.get('character')
    year = request.form.get('year')
    house = data['house']
    biography = request.form.get('biography')
    equipment = request.form.get('equipment')
    limit_images = int(request.form.get('limit_images'))
    images = data['images']
    
    if name and year and biography:
        if (character == None or character == '') and (equipment == None or equipment == ''):
            hero = {
                "name": name,
                "year": year,
                "house": house,
                "biography": biography,
                "images": images,
                "limit_images": limit_images
                }
        elif character == None or character == '':
             hero = {
                    "name": name,
                    "year": year,
                    "house": house,
                    "biography": biography,
                    "equipment": equipment,
                    "images": images,
                    "limit_images": limit_images
                }
        elif equipment == None or equipment == '':
            hero = {
                    "name": name,
                    "character": character,
                    "year": year,
                    "house": house,
                    "biography": biography,
                    "images": images,
                    "limit_images": limit_images
                }
        else:
            hero = {
                    "name": name,
                    "character": character,
                    "year": year,
                    "house": house,
                    "biography": biography,
                    "equipment": equipment,
                    "images": images,
                    "limit_images": limit_images
                }
        #Modificar heroe
        try:
            db.heroes.update_one({'_id': ObjectId(id)}, {'$set': hero }) 
            flash('Hero updated successfully!')
            return redirect('/hero/' + id)
        except Exception as err:
            print("An exception occurred :", err)
            flash('An error has occurred...')
            return redirect('/hero/' + id)
            
    
@app.route('/hero/<id>', methods=['GET'])
def get_hero(id):
    #Buscar en la bbdd
    hero = db.heroes.find_one({'_id': ObjectId(id)})
    #Convertir BSON a JSON
    data = json_util.dumps(hero)
    data = json_util.loads(data)
    #Arreglar un poco el texto de la biografia
    bio = data['biography'].lower()
    bio = bio.capitalize()
    #Truncar imagenes en base al limite que se le haya dado
    images = data['images']
    start = 0
    stop = data['limit_images']
    images = images[start:int(stop)]
    
    return render_template('detail.html', data=data, bio=bio, images=images) 
    
    
#En caso de error de ruta
@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'message': 'Resource Not Found: ' + request.url,
        'status': 404 
    })
    response.status_code = 404
    return response


if __name__ == "__main__":
    app.run(host='localhost', port='5000', debug=True)