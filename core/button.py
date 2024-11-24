import streamlit.components.v1 as components


def create_copy_button(text, button_id):
    copy_button_html = f"""
    <style>
    .copy-button {{
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 5px 10px;
        text-align: center;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        font-size: 14px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
        transition: background-color 0.3s;
    }}
    .copy-button.copied {{
        background-color: #555555;
    }}
    .copy-button span {{
        margin-left: 5px;
    }}
    </style>
    <button class="copy-button" onclick="copyToClipboard('poly_{button_id}', this)">
        📋 <span>Скопировать</span>
    </button>
    <input type="hidden" value="{text}" id="poly_{button_id}">
    <script>
    function copyToClipboard(elementId, btn) {{
        var copyText = document.getElementById(elementId).value;
        navigator.clipboard.writeText(copyText).then(function() {{
            btn.classList.add('copied');
            setTimeout(function() {{
                btn.classList.remove('copied');
            }}, 500);
        }}, function(err) {{
        }});
    }}
    </script>
    """
    components.html(copy_button_html, height=60, scrolling=False)