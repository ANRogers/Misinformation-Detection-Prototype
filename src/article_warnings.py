

def generate_warnings(result, source_status):
    warnings = []
    
    # source status warnings
    if source_status == 'unreliable':
        warnings.append("\nThis source has been flagged as unreliable. When reading articles from this source:")
        warnings.append("- Be skeptical of bold claims without evidence.")
        warnings.append("- Check if scientific claims are backed by recognized medical institutions.")
        warnings.append("- Be aware of emotionally charged language meant to provoke fear or outrage.")
        
    elif source_status == 'unknown':
        warnings.append("\nThe source is not recognized (unknown). When reading articles from unknown sources:")
        warnings.append("- Be extra cautious as the credibility is not verified.")
        warnings.append("- Look for clear author information and publication dates.")
        warnings.append("- Verify the article’s claims with trusted, well-known medical websites.")
        warnings.append("- Avoid sharing the article unless you have independently confirmed the information.")


    # found misleading
    if result['content_prediction'] == 0:
        warnings.append("\nThe article content has been flagged as potentially misleading. Watch out for:")
        warnings.append("- Exaggerated claims or miracle cures.")
        warnings.append("- Misrepresentation of scientific studies.")
        warnings.append("- Lack of credible references or citations.")
        warnings.append("- Cherry-picked data (only showing evidence that supports one view).")
        warnings.append("- Conspiracy theories or distrust in all mainstream medicine without strong evidence.")

    # low confidance
    if result['confidence'] <= 0.5:
        warnings.append("\nThe system has low confidence in its prediction.")
        warnings.append("- Interpretation should be cautious; consider getting a second opinion from verified health sources.")

    # Safe fallback
    if not warnings:
        warnings.append("No immediate risks detected. Content and source appear reliable.")

    return warnings


