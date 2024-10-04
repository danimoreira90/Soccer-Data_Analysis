from mplsoccer.pitch import Pitch

def test_pitch_creation():
    """Tenta criar um objeto Pitch e retorna o objeto junto com uma mensagem de erro se ocorrer falha."""
    try:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='white', figsize=(10, 7))
        print("Pitch created successfully!")
        return pitch, None
    except Exception as e:
        error_message = f"Error creating pitch: {str(e)}"
        print(error_message)
        return None, error_message
