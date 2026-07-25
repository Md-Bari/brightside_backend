from django.contrib import admin

from .models import KnowledgeFile, KnowledgeChunk


@admin.register(KnowledgeFile)
class KnowledgeFileAdmin(admin.ModelAdmin):
    list_display = ("title", "is_processed", "uploaded_at", "updated_at", "processed_at")
    search_fields = ("title",)


@admin.register(KnowledgeChunk)
class KnowledgeChunkAdmin(admin.ModelAdmin):
    list_display = ("knowledge_file", "chunk_index", "created_at", "updated_at")
    search_fields = ("chunk_text",)
