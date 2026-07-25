import os
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from apps.knowledgebase.services import KnowledgeBaseService


class Command(BaseCommand):
    help = "Import a local file into the knowledge base."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Absolute path to the file to import.")
        parser.add_argument("--title", type=str, help="Title for the knowledge file (defaults to filename).")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        title = options["title"]

        if not os.path.exists(file_path):
            raise CommandError(f"File not found at: {file_path}")

        try:
            self.stdout.write(self.style.NOTICE(f"Opening file: {file_path}"))
            filename = os.path.basename(file_path)
            
            with open(file_path, "rb") as f:
                django_file = File(f, name=filename)
                service = KnowledgeBaseService()
                
                self.stdout.write(self.style.NOTICE(f"Uploading and processing: {filename}"))
                knowledge_file = service.upload_and_process(title=title, uploaded_file=django_file)
                
            if knowledge_file.is_processed:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully processed knowledge file ID {knowledge_file.id}: '{knowledge_file.title}'"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Knowledge file uploaded (ID {knowledge_file.id}) but processing failed: {knowledge_file.processing_error}"
                    )
                )
        except Exception as e:
            raise CommandError(f"Error during import: {e}")
