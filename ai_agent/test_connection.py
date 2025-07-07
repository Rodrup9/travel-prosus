import os
from dotenv import load_dotenv
from groq import Groq

def test_groq_connection():
    """
    Prueba la conexión con Groq usando las credenciales del .env
    """
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Obtener API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Error: No se encontró GROQ_API_KEY en el archivo .env")
            return False
            
        # Inicializar el cliente
        client = Groq(api_key=api_key)
        
        # Hacer una llamada de prueba simple
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un asistente de viajes amigable."},
                {"role": "user", "content": "¿Cuál es tu modelo y qué puedes hacer?"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=1024
        )
        
        print("¡Conexión exitosa!")
        print("\nRespuesta del modelo:")
        print(completion.choices[0].message.content)
        return True
        
    except Exception as e:
        print(f"Error al conectar con Groq: {str(e)}")
        print("\nPor favor verifica:")
        print("1. Que el archivo .env existe y contiene GROQ_API_KEY")
        print("2. Que la API key es válida")
        print("3. Que el modelo especificado es correcto")
        return False

if __name__ == "__main__":
    test_groq_connection() 