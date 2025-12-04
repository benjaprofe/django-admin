from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Post, Categoria
from faker import Faker
import random
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
from pathlib import Path

fake = Faker('es_ES')  # Español de España


class Command(BaseCommand):
    help = 'Genera datos fake: 100 usuarios y posts de blog'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuarios',
            type=int,
            default=100,
            help='Número de usuarios a crear (default: 100)',
        )
        parser.add_argument(
            '--posts',
            type=int,
            default=200,
            help='Número de posts a crear (default: 200)',
        )

    def handle(self, *args, **options):
        num_usuarios = options['usuarios']
        num_posts = options['posts']

        self.stdout.write(self.style.SUCCESS('Iniciando generación de datos fake...'))

        # Crear categorías
        self.stdout.write('Creando categorías...')
        categorias_nombres = [
            'Tecnología', 'Programación', 'Diseño', 'Marketing',
            'Negocios', 'Educación', 'Salud', 'Viajes',
            'Cocina', 'Deportes', 'Arte', 'Música',
            'Ciencia', 'Filosofía', 'Historia', 'Literatura'
        ]
        
        categorias = []
        for nombre in categorias_nombres:
            categoria, created = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': fake.text(max_nb_chars=200)}
            )
            categorias.append(categoria)
            if created:
                self.stdout.write(f'  ✓ Categoría creada: {nombre}')

        # Crear usuarios
        self.stdout.write(f'\nCreando {num_usuarios} usuarios...')
        usuarios_creados = []
        credenciales = []  # Para guardar las contraseñas
        
        for i in range(num_usuarios):
            username = fake.user_name()
            # Asegurar que el username sea único
            while User.objects.filter(username=username).exists():
                username = fake.user_name()
            
            email = fake.email()
            # Asegurar que el email sea único
            while User.objects.filter(email=email).exists():
                email = fake.email()
            
            first_name = fake.first_name()
            last_name = fake.last_name()
            
            # Generar contraseña fake única
            password = fake.password(
                length=12,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True
            )
            
            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                date_joined=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.UTC)
            )
            usuarios_creados.append(usuario)
            credenciales.append({
                'username': username,
                'email': email,
                'password': password,
                'nombre': f'{first_name} {last_name}'
            })
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'  ✓ {i + 1}/{num_usuarios} usuarios creados')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ {len(usuarios_creados)} usuarios creados exitosamente'))
        
        # Guardar credenciales en archivo
        if credenciales:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            credenciales_file = base_dir / 'credenciales_usuarios.txt'
            
            with open(credenciales_file, 'w', encoding='utf-8') as f:
                f.write('=' * 70 + '\n')
                f.write('CREDENCIALES DE USUARIOS GENERADOS\n')
                f.write('=' * 70 + '\n\n')
                f.write(f'Total de usuarios: {len(credenciales)}\n')
                f.write(f'Generado el: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                f.write('-' * 70 + '\n\n')
                
                for idx, cred in enumerate(credenciales, 1):
                    f.write(f'Usuario #{idx}:\n')
                    f.write(f'  Username: {cred["username"]}\n')
                    f.write(f'  Email: {cred["email"]}\n')
                    f.write(f'  Nombre: {cred["nombre"]}\n')
                    f.write(f'  Contraseña: {cred["password"]}\n')
                    f.write('-' * 70 + '\n\n')
            
            self.stdout.write(self.style.SUCCESS(f'✓ Credenciales guardadas en: {credenciales_file}'))

        # Crear posts
        self.stdout.write(f'\nCreando {num_posts} posts...')
        posts_creados = 0
        
        for i in range(num_posts):
            titulo = fake.sentence(nb_words=6).rstrip('.')
            # Asegurar que el slug sea único
            slug_base = slugify(titulo)
            slug = slug_base
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{slug_base}-{counter}"
                counter += 1
            
            autor = random.choice(usuarios_creados)
            categoria = random.choice(categorias) if random.random() > 0.1 else None  # 90% con categoría
            
            # Generar contenido más largo y realista
            contenido = '\n\n'.join([
                fake.paragraph(nb_sentences=5),
                fake.paragraph(nb_sentences=8),
                fake.paragraph(nb_sentences=6),
            ])
            
            # Fecha de creación aleatoria en los últimos 2 años
            fecha_creacion = fake.date_time_between(
                start_date='-2y',
                end_date='now',
                tzinfo=timezone.UTC
            )
            
            # 80% de los posts publicados
            publicado = random.random() > 0.2
            fecha_publicacion = None
            if publicado:
                fecha_publicacion = fecha_creacion + timedelta(
                    days=random.randint(0, 30)
                )
            
            post = Post.objects.create(
                titulo=titulo,
                slug=slug,
                autor=autor,
                categoria=categoria,
                contenido=contenido,
                publicado=publicado,
                fecha_publicacion=fecha_publicacion,
                visitas=random.randint(0, 5000) if publicado else 0,
            )
            
            # Actualizar fecha_creacion manualmente
            Post.objects.filter(id=post.id).update(fecha_creacion=fecha_creacion)
            
            posts_creados += 1
            
            if (i + 1) % 20 == 0:
                self.stdout.write(f'  ✓ {i + 1}/{num_posts} posts creados')

        self.stdout.write(self.style.SUCCESS(f'\n✓ {posts_creados} posts creados exitosamente'))

        # Resumen
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('RESUMEN:'))
        self.stdout.write(self.style.SUCCESS(f'  - Usuarios creados: {len(usuarios_creados)}'))
        self.stdout.write(self.style.SUCCESS(f'  - Posts creados: {posts_creados}'))
        self.stdout.write(self.style.SUCCESS(f'  - Categorías: {len(categorias)}'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.WARNING('\n⚠️  IMPORTANTE: Las contraseñas de los usuarios se han guardado en el archivo credenciales_usuarios.txt'))
        self.stdout.write(self.style.WARNING('    Cada usuario tiene una contraseña única generada automáticamente.'))

