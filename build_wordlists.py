#!/usr/bin/env python3
"""
Fetch frequency word lists from Wiktionary and generate wordlists.js
for the anagram finder application.
"""

import urllib.request
import re
import json
import html
import ssl

# Bypass SSL verification (macOS Python often has certificate issues)
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# ============================================================
# ENGLISH - TV/Movie Scripts (2006), top 3000
# ============================================================
def fetch_english():
    """Fetch English words from Wiktionary TV/Movie frequency lists."""
    words = []
    urls = [
        "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/TV/2006/1-1000",
        "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/TV/2006/1001-2000",
        "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/TV/2006/2001-3000",
        "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/TV/2006/3001-4000",
        "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/TV/2006/4001-5000",
    ]
    
    for url in urls:
        print(f"  Fetching: {url}")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as resp:
                page = resp.read().decode('utf-8')
            
            # The words are in table rows: <td>word</td> or <td><a ...>word</a></td>
            # Pattern: | rank | word | count | in wiki table
            # Look for table cells with words
            # The HTML has <tr><td>rank</td><td>word or link</td><td>count</td></tr>
            rows = re.findall(r'<tr>\s*<td>(\d+)\s*</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>', page, re.DOTALL)
            
            for rank, word_cell, count_cell in rows:
                # Extract text from the word cell (may contain links, "or" alternatives, etc.)
                # Remove HTML tags
                word_text = re.sub(r'<[^>]+>', '', word_cell).strip()
                # Take first word before "or", "'s", spaces with special chars
                # Handle cases like "a or A .", "house or House", etc.
                word_text = word_text.split(' or ')[0].strip()
                word_text = word_text.split(' . ')[0].strip()
                word_text = word_text.rstrip(' .')
                # Remove possessives and contractions for cleaner anagram matching
                # But keep contractions like "don't", "can't" etc - actually skip those
                word = word_text.strip().lower()
                if word:
                    words.append(word)
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
    
    return words


# ============================================================
# SWEDISH - Parole corpus, top 5000
# ============================================================
def fetch_swedish():
    """Fetch Swedish words from Wiktionary Parole frequency list."""
    url = "https://sv.wiktionary.org/wiki/Wiktionary:Projekt/Frekvensordlista/Parole_rad_1-5000"
    print(f"  Fetching: {url}")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as resp:
            page = resp.read().decode('utf-8')
        
        # Get content section
        idx = page.find('mw-parser-output')
        content = page[idx:]
        
        # Words are in WikiLink anchors with title attributes
        # Format: rel="mw:WikiLink" ... title="word" ... >word</a>
        words = re.findall(r'rel="mw:WikiLink"[^>]*title="([^"]+)"', content)
        
        return [w.strip().lower() for w in words if w.strip()]
    except Exception as e:
        print(f"  Error fetching Swedish: {e}")
        return []


# ============================================================
# DANISH - OpenSubtitles wordlist
# ============================================================
def fetch_danish():
    """Fetch Danish words from Wiktionary Danish wordlist."""
    url = "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Danish_wordlist"
    print(f"  Fetching: {url}")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as resp:
            page = resp.read().decode('utf-8')
        
        # Format: <li><span lang="da"><a href="/wiki/word#Danish" title="word">word</a></span> freq</li>
        words = re.findall(r'<li><span lang="da"><a[^>]*>([^<]+)</a></span>\s*\d+</li>', page)
        
        return [w.strip().lower() for w in words if w.strip()]
    except Exception as e:
        print(f"  Error fetching Danish: {e}")
        return []


# ============================================================
# DUTCH - OpenSubtitles wordlist  
# ============================================================
def fetch_dutch():
    """Fetch Dutch words from Wiktionary Dutch wordlist."""
    url = "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Dutch_wordlist"
    print(f"  Fetching: {url}")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as resp:
            page = resp.read().decode('utf-8')
        
        # Format: <li><span lang="nl"><a href="/wiki/word#Dutch" title="word">word</a></span> freq</li>
        words = re.findall(r'<li><span lang="nl"><a[^>]*>([^<]+)</a></span>\s*\d+</li>', page)
        
        return [w.strip().lower() for w in words if w.strip()]
    except Exception as e:
        print(f"  Error fetching Dutch: {e}")
        return []


# ============================================================
# FILTERING
# ============================================================

# Common English names to filter out from all lists
NAMES = {
    'jack', 'sam', 'leo', 'theresa', 'carly', 'ethan', 'paul', 'david',
    'jake', 'al', 'michael', 'max', 'luis', 'natalie', 'grace', 'frank',
    'lucy', 'sheridan', 'ben', 'julian', 'joey', 'antonio', 'jason',
    'george', 'ross', 'brooke', 'todd', 'niles', 'craig', 'billy',
    'ray', 'bo', 'angel', 'nick', 'miguel', 'cristian', 'greenlee',
    'phoebe', 'luke', 'emily', 'timmy', 'chris', 'kay', 'jerry',
    'richard', 'ryan', 'lindsay', 'victor', 'nora', 'beth', 'alison',
    'rick', 'frasier', 'danny', 'tony', 'kevin', 'buffy', 'rafe',
    'erica', 'brenda', 'jim', 'blair', 'laura', 'sabrina', 'phillip',
    'eric', 'olivia', 'cassie', 'aaron', 'kendall', 'tom', 'josh',
    'simon', 'hal', 'edmund', 'brady', 'troy', 'mary', 'courtney',
    'alan', 'paris', 'joe', 'tim', 'bob', 'roz', 'mitch', 'rory',
    'ivy', 'adam', 'mike', 'chloe', 'barbara', 'kate', 'liz', 'ian',
    'henry', 'phyllis', 'mac', 'maria', 'isaac', 'anna', 'simone',
    'amber', 'pacey', 'liza', 'daphne', 'whitney', 'chad', 'katie',
    'colleen', 'bianca', 'paige', 'viki', 'chandler', 'nikolas',
    'starr', 'kyle', 'alex', 'elizabeth', 'charlie', 'karen', 'skye',
    'molly', 'diane', 'bridget', 'brad', 'livvie', 'eddie', 'rebecca',
    'sharon', 'jennifer', 'philip', 'elaine', 'rachel', 'salem',
    'stephen', 'ricky', 'raul', 'harley', 'daniel', 'stan', 'julia',
    'pete', 'lucas', 'jan', 'abby', 'sean', 'lee', 'don', 'donna',
    'malcolm', 'newman', 'maureen', 'oakdale', 'ted', 'susan',
    'kristina', 'casey', 'nancy', 'xander', 'giles', 'cartman',
    'lizzie', 'aidan', 'mateo', 'carmen', 'diana', 'sydney', 'jackie',
    'maggie', 'lewis', 'johnny', 'tabitha', 'lisa', 'ashley', 'morgan',
    'lorelai', 'peg', 'zack', 'kim', 'nicole', 'allison', 'forrester',
    'isabella', 'lexie', 'sami', 'lily', 'edward', 'diego', 'cole',
    'kenny', 'bobby', 'sally', 'stephanie', 'parker', 'toby',
    'helena', 'jackson', 'victoria', 'marshall', 'daria', 'roger',
    'gus', 'santos', 'annie', 'laurence', 'abe', 'dan',
    'russell', 'montgomery', 'bryant', 'walter', 'tommy', 'matt',
    'phil', 'helen', 'jane', 'william', 'mimi', 'audrey', 'marty',
    'greta', 'barry', 'wesley', 'nate', 'quinn', 'zelda', 'fred',
    'carl', 'margaret', 'homer', 'laurie', 'jenny', 'colby', 'bart',
    'claire', 'logan', 'thomas', 'snyder', 'robert', 'harold',
    'randy', 'palmer', 'jamie', 'mackenzie', 'proteus',
    'spaulding', 'buchanan', 'alcazar', 'kramer', 'martin',
    'taylor', 'neil', 'harry', 'andy', 'jess', 'colin', 'amanda',
    'fraser', 'caleb', 'seth', 'rosanna', 'peter', 'amy', 'brian',
    'hank', 'reva', 'stenbeck', 'gwen', 'trey', 'baldwin',
    'nikki', 'caroline', 'rae', 'abbott', 'carter',
    'tess', 'scott', 'michelle', 'ned', 'bonnie', 'austin',
    'keri', 'vanessa', 'larry', 'prue', 'jill',
    'charles', 'jax', 'jessica', 'dawson', 'alexis', 'shawn',
    'monica', 'steve', 'margo', 'dixon', 'rex', 'tory',
    'llanview', 'kane', 'alexandra', 'hilda', 'mia',
    'maris', 'marah',
    # Swedish names
    'jan', 'gunilla', 'bryssel', 'ryssland', 'joakim', 'köpenhamn',
    'sollentuna', 'luleå', 'berlin', 'cecilia', 'kroatien',
    'camilla', 'jönköping', 'peking', 'frida', 'sture',
    'lundgren', 'hansson', 'moskva', 'anne',
    # Danish names  
    'charlie', 'kate', 'washington', 'ryan', 'francisco',
    'frodo', 'aragorn', 'bond', 'batman',
    # Dutch names
    'londen', 'adam', 'pete', 'jason', 'manhattan', 'charlotte',
    'berlijn', 'duitsland',
}

def is_valid_word(word, lang='en'):
    """Check if a word is valid for the anagram finder."""
    if not word or len(word) < 2:
        return False
    
    # Skip if it's a known name
    if word in NAMES:
        return False
    
    # Skip words with apostrophes, hyphens, spaces, numbers, dots
    if any(c in word for c in "''-. 0123456789"):
        return False
    
    # Skip single letters and abbreviations (all caps when original is checked)
    if len(word) <= 1:
        return False
    
    # Skip common abbreviations
    abbrevs = {'tv', 'ok', 'dna', 'fbi', 'la', 'st', 'mr', 'mrs', 'ms', 'dr',
               'vs', 'etc', 'usa', 'uk', 'eu', 'fn', 'ff', 'cm', 'km', 'kg',
               'nbsp', 'lt', 'co', 'de', 'non', 'th', 're', 'ed', 'er',
               'hm', 'uh', 'um', 'ah', 'oh', 'eh', 'shh', 'heh', 'ya',
               'yo', 'ow', 'aw', 'mm', 'mmm', 'hmm', 'ooh', 'ohh', 'ahh',
               'aah', 'whoo', 'uhh', 'umm', 'gee', 'ugh', 'nah', 'huh',
               'yep', 'nope', 'ahem', 'whoa', 'blah', 'pga', 'sk'}
    if word in abbrevs:
        return False
    
    # For non-English languages, check valid characters
    if lang == 'sv':
        if not re.match(r'^[a-zåäö]+$', word):
            return False
    elif lang == 'da':
        if not re.match(r'^[a-zæøå]+$', word):
            return False
    elif lang == 'nl':
        if not re.match(r'^[a-zëïéèêüö]+$', word):
            return False
    elif lang == 'en':
        if not re.match(r'^[a-z]+$', word):
            return False
    
    return True


def clean_wordlist(words, lang='en'):
    """Clean and deduplicate a word list."""
    seen = set()
    cleaned = []
    for word in words:
        word = word.strip().lower()
        if word not in seen and is_valid_word(word, lang):
            seen.add(word)
            cleaned.append(word)
    return cleaned


def generate_js(sv_words, da_words, en_words, nl_words):
    """Generate the wordlists.js file."""
    lines = []
    lines.append("const WORDLISTS = {")
    
    # Swedish
    lines.append("  sv: [")
    for i in range(0, len(sv_words), 10):
        chunk = sv_words[i:i+10]
        line = ", ".join(f'"{w}"' for w in chunk)
        lines.append(f"    {line},")
    lines.append("  ],")
    
    # Danish
    lines.append("  da: [")
    for i in range(0, len(da_words), 10):
        chunk = da_words[i:i+10]
        line = ", ".join(f'"{w}"' for w in chunk)
        lines.append(f"    {line},")
    lines.append("  ],")
    
    # English
    lines.append("  en: [")
    for i in range(0, len(en_words), 10):
        chunk = en_words[i:i+10]
        line = ", ".join(f'"{w}"' for w in chunk)
        lines.append(f"    {line},")
    lines.append("  ],")
    
    # Dutch
    lines.append("  nl: [")
    for i in range(0, len(nl_words), 10):
        chunk = nl_words[i:i+10]
        line = ", ".join(f'"{w}"' for w in chunk)
        lines.append(f"    {line},")
    lines.append("  ],")
    
    lines.append("};")
    lines.append("")
    lines.append("console.log('Wordlists loaded successfully');")
    lines.append("console.log('Swedish:', WORDLISTS.sv.length, 'words');")
    lines.append("console.log('Danish:', WORDLISTS.da.length, 'words');")
    lines.append("console.log('English:', WORDLISTS.en.length, 'words');")
    lines.append("console.log('Dutch:', WORDLISTS.nl.length, 'words');")
    lines.append("")
    
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("Building wordlists from Wiktionary frequency lists")
    print("=" * 60)
    
    print("\n📖 Fetching English words...")
    en_raw = fetch_english()
    print(f"  Raw: {len(en_raw)} words")
    en_words = clean_wordlist(en_raw, 'en')
    print(f"  Cleaned: {len(en_words)} words")
    
    print("\n📖 Fetching Swedish words...")
    sv_raw = fetch_swedish()
    print(f"  Raw: {len(sv_raw)} words")
    sv_words = clean_wordlist(sv_raw, 'sv')
    print(f"  Cleaned: {len(sv_words)} words")
    
    print("\n📖 Fetching Danish words...")
    da_raw = fetch_danish()
    print(f"  Raw: {len(da_raw)} words")
    da_words = clean_wordlist(da_raw, 'da')
    print(f"  Cleaned: {len(da_words)} words")
    
    print("\n📖 Fetching Dutch words...")
    nl_raw = fetch_dutch()
    print(f"  Raw: {len(nl_raw)} words")
    nl_words = clean_wordlist(nl_raw, 'nl')
    print(f"  Cleaned: {len(nl_words)} words")
    
    print("\n📝 Generating wordlists.js...")
    js_content = generate_js(sv_words, da_words, en_words, nl_words)
    
    with open('/Users/micke/code/anagram/wordlists.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"\n✅ wordlists.js generated successfully!")
    print(f"  Swedish: {len(sv_words)} words")
    print(f"  Danish:  {len(da_words)} words")
    print(f"  English: {len(en_words)} words")
    print(f"  Dutch:   {len(nl_words)} words")
    print(f"  Total:   {len(sv_words) + len(da_words) + len(en_words) + len(nl_words)} words")


if __name__ == '__main__':
    main()
