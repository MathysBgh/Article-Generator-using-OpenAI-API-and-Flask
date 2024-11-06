from flask import Flask, request, render_template, jsonify
import os
from langchain_openai import ChatOpenAI

# Clé API pour OpenAI
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "<votre_cle_openai>")

# Remplacez "<votre_cle_langsmith>" par votre clé API LangSmith
os.environ['LANGCHAIN_TRACING_V2'] = "true"
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY', '<votre_cle_langsmith>')
# Initialisation du modèle
model = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.9,
    max_tokens=200
)

app = Flask(__name__)

def generate_article_structure(subject):
    prompt = f"Je souhaite écrire un article sur le sujet suivant : '{subject}'. Donne-moi un titre accrocheur et une structure avec des titres de sections appropriés pour l'article ne donne pas de conclusion ni introduction."
    response = model.invoke(prompt)
    response_text = response.content.strip()
    lines = response_text.split('\n')
    title = lines[0].replace("Titre: ", "").strip()
    sections = [line.replace("- ", "").strip() for line in lines[1:] if line]
    return {"title": title, "sections": sections}

def generate_section_content(title, sections, section_title):
    prompt = (f"L'article s'intitule '{title}'. Voici la structure complète de l'article : {', '.join(sections)}. "
              f"Génère le contenu de la section intitulée '{section_title}'.")
    response = model.invoke(prompt)
    return response.content.strip()

def generate_intro_conclusion(title, sections):
    full_content = "\n\n".join([f"{section_title}: {section_content}" for section_title, section_content in sections.items()])
    intro_prompt = f"Écris une introduction pour un article intitulé '{title}' basé sur le contenu suivant:\n{full_content}\n\nIntroduction:"
    introduction = model.invoke(intro_prompt).content.strip()
    conclusion_prompt = f"Écris une conclusion pour un article intitulé '{title}' basé sur le contenu suivant:\n{full_content}\n\nConclusion:"
    conclusion = model.invoke(conclusion_prompt).content.strip()
    return {"introduction": introduction, "conclusion": conclusion}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-article', methods=['POST'])
@app.route('/generate-article', methods=['POST'])
def generate_article():
    subject = request.form.get('subject')
    if not subject:
        return jsonify({"error": "Sujet manquant"}), 400

    # Générer la structure de l'article
    article_structure = generate_article_structure(subject)

    # Générer le contenu de chaque section
    sections_content = {section: generate_section_content(article_structure['title'], article_structure['sections'], section) for section in article_structure['sections']}

    # Générer l'introduction et la conclusion
    intro_conclusion = generate_intro_conclusion(article_structure['title'], sections_content)

    # Générer le sommaire numéroté
    article_md = f"<h1>{article_structure['title']}</h1>"
    article_md += "<h2>Sommaire</h2>"
    article_md += "<ol>"
    for i, section_title in enumerate(article_structure['sections'], start=1):
        article_md += f"<li>{section_title}</li>"
    article_md += "</ol>"

    # Ajouter l'introduction
    article_md += "<h2>Introduction</h2>"
    article_md += f"<p>{intro_conclusion['introduction']}</p>"

    # Ajouter les sections
    for section_title, section_content in sections_content.items():
        article_md += f"<h2>{section_title}</h2>"
        article_md += f"<p>{section_content}</p>"

    # Ajouter la conclusion
    article_md += "<h2>Conclusion</h2>"
    article_md += f"<p>{intro_conclusion['conclusion']}</p>"

    return jsonify({"article": article_md})

if __name__ == '__main__':
    app.run(debug=True)
