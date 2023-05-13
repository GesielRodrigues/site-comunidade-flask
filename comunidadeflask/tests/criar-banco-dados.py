from comunidadeflask import app, database

# Comando para criar o banco de dados
with app.app_context():
    database.drop_all()
    database.create_all()
