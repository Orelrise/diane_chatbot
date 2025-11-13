"""
Validation service to detect off-topic questions before calling Groq API.
This helps save API tokens by filtering out irrelevant questions early.
"""

from typing import Tuple


# Keywords that indicate off-topic questions
OFF_TOPIC_KEYWORDS = {
    # Politics & Current Events
    "politique", "élection", "président", "gouvernement", "parti", "vote",
    "actualité", "actualités", "news", "journal",

    # Sports
    "football", "rugby", "tennis", "sport", "match", "équipe", "joueur",
    "championnat", "coupe", "olympique",

    # Technology & Programming
    "code", "programmation", "python", "javascript", "ordinateur", "logiciel",
    "application", "site web", "internet", "wifi", "smartphone",

    # Cooking (non-herbal)
    "recette", "cuisine", "cuisson", "four", "poêle", "restaurant",
    "gastronomie", "chef",

    # Entertainment
    "film", "série", "cinéma", "musique", "concert", "chanson",
    "télévision", "streaming", "netflix",

    # Finance
    "bourse", "crypto", "bitcoin", "investissement", "action", "banque",

    # Travel
    "voyage", "hôtel", "avion", "tourisme", "vacances", "destination",

    # General non-herbal topics
    "météo", "weather", "voiture", "automobile", "immobilier",
}

# Keywords that strongly indicate herbal/medicinal plant topics
HERBAL_KEYWORDS = {
    "plante", "plantes", "herbe", "herbes", "tisane", "tisanes",
    "infusion", "décoction", "phytothérapie", "herboristerie",
    "médicinal", "médicinale", "remède", "remèdes",
    "fleur", "fleurs", "racine", "racines", "feuille", "feuilles",
    "propriété", "propriétés", "bienfait", "bienfaits",
    "camomille", "valériane", "passiflore", "menthe", "thym",
    "romarin", "lavande", "sauge", "tilleul", "verveine",
    "gingembre", "curcuma", "echinacea", "millepertuis",
    "sommeil", "stress", "digestion", "anxiété", "insomnie",
    "inflammation", "douleur", "immunité", "détox",
    "bio", "naturel", "naturelle", "traditionnel",
}


def is_valid_herbalism_topic(message: str) -> Tuple[bool, str]:
    """
    Validate if a message is about herbalism/medicinal plants.

    Args:
        message: User's question

    Returns:
        Tuple of (is_valid, reason)
        - is_valid: True if topic is valid, False otherwise
        - reason: Explanation of validation result
    """
    message_lower = message.lower()

    # Check for very short messages
    if len(message.strip()) < 3:
        return False, "Message too short"

    # Check for clear off-topic keywords
    off_topic_found = [kw for kw in OFF_TOPIC_KEYWORDS if kw in message_lower]
    if off_topic_found:
        return False, f"Off-topic keywords detected: {', '.join(off_topic_found[:3])}"

    # Check for herbal keywords (positive indication)
    herbal_found = [kw for kw in HERBAL_KEYWORDS if kw in message_lower]
    if herbal_found:
        return True, f"Herbal keywords detected: {', '.join(herbal_found[:3])}"

    # If no clear indicators, assume it might be valid
    # (Let Diane's system prompt handle edge cases)
    return True, "No clear off-topic indicators, allowing through"


def get_off_topic_response() -> str:
    """
    Get the standardized off-topic response.

    Returns:
        HTML formatted off-topic response
    """
    return "<p>Je suis désolée, mais je suis spécialisée exclusivement en herboristerie et plantes médicinales. Avez-vous une question sur les plantes médicinales ?</p>"
