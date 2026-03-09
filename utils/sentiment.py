def is_negative(text: str) -> bool:
    text = text.lower()

    negative_keywords = [
        "nul", "nulle", "ça ne marche pas", "marche pas",
        "incompréhensible", "tu ne comprends rien",
        "pas satisfait", "pas satisfaite",
        "frustré", "frustrée",
        "c'est mauvais", "mauvais service",
        "je suis déçu", "je suis déçue",
        "horrible", "catastrophique", "inadmissible",
        "problème", "bug", "erreur"
    ]

    return any(kw in text for kw in negative_keywords)
