# Dockerfile autonome pour API LLM avec Ollama et Mistral
FROM ollama/ollama:latest

# Installer Python et les dépendances système
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Créer un environnement virtuel Python
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Configurer le répertoire de travail
WORKDIR /app

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY app/ ./app/

# Télécharger le modèle Mistral pendant la construction de l'image
RUN ollama serve & \
    sleep 10 && \
    ollama pull mistral && \
    sleep 5 && \
    pkill ollama

# Créer un script de démarrage simplifié qui lance seulement Ollama et l'API
RUN cat > /app/init.sh << 'EOF'
#!/bin/bash
set -e

echo "=== Démarrage du container ==="

# Démarrer Ollama en arrière-plan
echo "Démarrage d'Ollama..."
ollama serve &
OLLAMA_PID=$!

# Fonction pour nettoyer les processus
cleanup() {
    echo "Arrêt des services..."
    kill $OLLAMA_PID 2>/dev/null || true
    exit
}
trap cleanup SIGTERM SIGINT

# Attendre qu'Ollama soit prêt
echo "Attente du démarrage d'Ollama..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "Ollama est prêt !"
        break
    fi
    echo "Tentative $i/30 - Ollama démarre..."
    sleep 2
done

# Vérifier si Ollama répond
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Erreur: Ollama ne répond pas après 60 secondes"
    exit 1
fi

# Vérifier que le modèle Mistral est bien présent
echo "Vérification de la présence du modèle Mistral..."
ollama list

# Démarrer l'API FastAPI
echo "Démarrage de l'API FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
EOF

# Rendre le script exécutable
RUN chmod +x /app/init.sh

# Exposer les ports
EXPOSE 8000 11434

# Variables d'environnement
ENV OLLAMA_BASE_URL=http://localhost:11434
ENV DEFAULT_MODEL=mistral

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health && curl -f http://localhost:11434/api/tags || exit 1

# Remplacer l'entrypoint et utiliser notre script
ENTRYPOINT []
CMD ["/bin/bash", "/app/init.sh"]
