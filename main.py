from database.user import User
from database.database import Session, init_db

def main():
    # Inicializar la base de datos
    init_db()

    # Crear una sesión
    session = Session()

    try:
        # Crear usuarios
        alice = User("alice", "lala", "alice@example.com")
        bob = User("bob", "lala", "bob@example.com")
        charlie = User("charlie", "lala", "charlie@example.com")

        session.add_all([alice, bob, charlie])
        session.commit()

        # Alice sigue a Bob y Charlie
        alice.follow(bob)
        alice.follow(charlie)
        session.commit()

        # Bob sigue a Alice
        bob.follow(alice)
        session.commit()

        # Imprimir información de seguimiento
        print(f"Alice sigue a {alice.following_count()} usuarios")
        print(f"Alice tiene {alice.followers_count()} seguidores")
        print(f"Bob sigue a {bob.following_count()} usuarios")
        print(f"Bob tiene {bob.followers_count()} seguidores")
        print(f"Charlie sigue a {charlie.following_count()} usuarios")
        print(f"Charlie tiene {charlie.followers_count()} seguidores")

        # Verificar si Alice sigue a Bob y Charlie
        print(f"Alice sigue a Bob: {alice.is_following(bob)}")
        print(f"Alice sigue a Charlie: {alice.is_following(charlie)}")

        # Alice deja de seguir a Charlie
        alice.unfollow(charlie)
        session.commit()

        print(f"Después de dejar de seguir, Alice sigue a {alice.following_count()} usuarios")
        print(f"Alice sigue a Charlie: {alice.is_following(charlie)}")

        # Listar seguidores de Bob
        print("Seguidores de Bob:")
        for follower in bob.followers:
            print(f"- {follower.username}")

        # Listar a quienes sigue Alice
        print("Alice sigue a:")
        for followed in alice.following:
            print(f"- {followed.username}")

        alice.upload_post(session, "Hola, soy Alice")
        alice.get_posts()
        session.commit()


    finally:
        # Cerrar la sesión
        session.close()

if __name__ == "__main__":
    main()
