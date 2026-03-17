// Normalisera och sortera bokstäver för anagramjämförelse
function normalizeWord(word) {
    return word
        .toLowerCase()
        .replace(/[^a-zäöåæøëïéèêü]/g, '')
        .split('')
        .sort()
        .join('');
}

// Räkna bokstäver i ett ord → { a: 2, b: 1, ... }
function letterCounts(word) {
    const counts = {};
    for (const ch of word.toLowerCase().replace(/[^a-zäöåæøëïéèêü]/g, '')) {
        counts[ch] = (counts[ch] || 0) + 1;
    }
    return counts;
}

// Subtrahera bokstavsräkning b från a. Returnera null om det inte går.
function subtractCounts(a, b) {
    const result = { ...a };
    for (const ch in b) {
        if (!result[ch] || result[ch] < b[ch]) return null;
        result[ch] -= b[ch];
        if (result[ch] === 0) delete result[ch];
    }
    return result;
}

// Är bokstavsräkningen tom?
function isEmpty(counts) {
    return Object.keys(counts).length === 0;
}

// Hitta enstaka anagram (alla bokstäver)
function findAnagrams(letters, wordList) {
    const normalized = normalizeWord(letters);
    
    if (normalized.length === 0) {
        return [];
    }

    return wordList.filter(word => {
        return normalizeWord(word) === normalized;
    });
}

// Vanliga korta ord (1–2 bokstäver) per språk – filtrerar bort förkortningar som "dn", "gp"
const SHORT_WORDS = {
    sv: new Set(['i', 'å', 'av', 'på', 'en', 'an', 'om', 'du', 'nu', 'ni', 'vi', 'ha', 'se', 'ge', 'ta', 'gå', 'få', 'ny', 'ju', 'ja', 'då', 'så', 'ur', 'ut', 'in', 'el', 'by', 'ro', 'öl', 'ej', 'le', 'nå', 'må', 'do', 'ön', 'år', 'är', 'åt', 'sa', 'än']),
    da: new Set(['i', 'af', 'at', 'da', 'de', 'du', 'en', 'er', 'et', 'fo', 'ha', 'he', 'jo', 'ja', 'nu', 'ny', 'om', 'op', 'på', 'se', 'så', 'to', 'ud', 'vi', 'år', 'og', 'no', 'al', 'ad']),
    en: new Set(['a', 'i', 'am', 'an', 'as', 'at', 'be', 'by', 'do', 'go', 'ha', 'he', 'hi', 'if', 'in', 'is', 'it', 'me', 'my', 'no', 'of', 'on', 'or', 'so', 'to', 'up', 'us', 'we']),
    nl: new Set(['ik', 'je', 'de', 'op', 'al', 'om', 'is', 'er', 'nu', 'na', 'ze', 'we', 'zo', 'ja', 'af', 'in', 'en', 'te', 'of', 'an', 'ga', 'al', 'he', 'me', 'uw', 'uw', 'no', 'do'])
};

// Hitta multi-ord-kombinationer som använder ALLA bokstäver
function findMultiWordAnagrams(letters, wordList, maxWords = 3) {
    const inputCounts = letterCounts(letters);
    const inputLen = normalizeWord(letters).length;
    
    if (inputLen < 4) return []; // För kort för kombinationer

    // Avgör språk genom att kolla vilken ordlista som matchar
    let lang = 'en';
    for (const [code, list] of Object.entries(WORDLISTS)) {
        if (list === wordList) { lang = code; break; }
    }
    const allowedShort = SHORT_WORDS[lang] || new Set();

    // Förfiltrera: behåll bara ord vars bokstäver finns i input och som är kortare
    // Korta ord (1–2 bokstäver) tillåts bara om de finns i vitlistan
    const candidates = [];
    for (const word of wordList) {
        const norm = normalizeWord(word);
        if (norm.length < 1 || norm.length >= inputLen) continue;
        if (norm.length <= 2 && !allowedShort.has(word.toLowerCase())) continue;
        const wc = letterCounts(word);
        if (subtractCounts(inputCounts, wc) !== null) {
            candidates.push({ word, norm, counts: wc, len: norm.length });
        }
    }

    // Sortera kandidater efter längd (längst först) för bättre pruning
    candidates.sort((a, b) => b.len - a.len);

    const results = [];
    const seen = new Set();
    const MAX_RESULTS = 100;
    const startTime = Date.now();
    const TIME_LIMIT = maxWords > 3 ? 15000 : 3000; // 15s för långa, 3s för standard

    // Rekursiv sökning
    function search(remaining, combo, startIdx, depth) {
        if (results.length >= MAX_RESULTS) return;
        if (Date.now() - startTime > TIME_LIMIT) return;
        if (isEmpty(remaining)) {
            // Sortera orden i kombinationen för att undvika dubbletter
            const key = combo.map(w => w.word).sort().join(' + ');
            if (!seen.has(key)) {
                seen.add(key);
                results.push(combo.map(w => w.word));
            }
            return;
        }
        if (depth >= maxWords) return;

        for (let i = startIdx; i < candidates.length; i++) {
            if (results.length >= MAX_RESULTS) return;
            const cand = candidates[i];
            const rest = subtractCounts(remaining, cand.counts);
            if (rest !== null) {
                search(rest, [...combo, cand], i + 1, depth + 1);
            }
        }
    }

    search(inputCounts, [], 0, 0);
    return results;
}

// Hämta valda språk
function getSelectedLanguages() {
    const checkboxes = document.querySelectorAll('input[name="language"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// Visa resultaten
function displayResults(singleResults, multiResults) {
    const resultsDiv = document.getElementById('results');
    
    if (singleResults.length === 0 && multiResults.length === 0) {
        resultsDiv.innerHTML = '<p class="no-results">Inga anagram funna. Försök med andra bokstäver!</p>';
        return;
    }

    let html = '';

    // Enstaka ord
    if (singleResults.length > 0) {
        html += '<h3 class="results-heading">Hela ord</h3>';
        html += '<div class="results-grid">';
        singleResults.forEach(result => {
            html += `
                <div class="result-word">
                    ${result.word}
                    <div class="result-language">${getLanguageName(result.language)}</div>
                </div>
            `;
        });
        html += '</div>';
    }

    // Multi-ord-kombinationer
    if (multiResults.length > 0) {
        html += '<h3 class="results-heading combo-heading">Kombinationer</h3>';
        html += '<div class="combo-list">';
        multiResults.forEach(result => {
            const wordsHtml = result.words.map(w => `<span class="combo-word">${w}</span>`).join(' + ');
            html += `
                <div class="combo-result">
                    <div class="combo-words">${wordsHtml}</div>
                    <div class="result-language">${getLanguageName(result.language)}</div>
                </div>
            `;
        });
        html += '</div>';
    }

    resultsDiv.innerHTML = html;
}

// Språknamn
function getLanguageName(code) {
    const names = {
        'sv': '🇸🇪 Svenska',
        'da': '🇩🇰 Danska',
        'en': '🇬🇧 Engelska',
        'nl': '🇳🇱 Nederländska'
    };
    return names[code] || code;
}

// Sök anagram
function searchAnagrams() {
    const input = document.getElementById('letterInput').value;
    const selectedLanguages = getSelectedLanguages();
    const resultsDiv = document.getElementById('results');

    if (!input.trim()) {
        resultsDiv.innerHTML = '<p class="info-text">Skriv in bokstäver för att börja söka</p>';
        return;
    }

    if (selectedLanguages.length === 0) {
        resultsDiv.innerHTML = '<p class="error">Välj minst ett språk!</p>';
        return;
    }

    // Kolla om långa kombinationer är aktiverat
    const longCombos = document.getElementById('longCombos').checked;
    const maxWords = longCombos ? 5 : 3;

    resultsDiv.innerHTML = longCombos
        ? '<p class="loading">Söker långa kombinationer – kan ta upp till 15 sekunder...</p>'
        : '<p class="loading">Söker...</p>';

    // Kör sökningen asynkront så att "Söker..." hinner visas
    setTimeout(() => {
        const singleResults = [];
        const multiResults = [];

        selectedLanguages.forEach(lang => {
            const wordList = WORDLISTS[lang] || [];

            // Enstaka hela ord
            const anagrams = findAnagrams(input, wordList);
            anagrams.forEach(word => {
                singleResults.push({ word, language: lang });
            });

            // Multi-ord-kombinationer
            const combos = findMultiWordAnagrams(input, wordList, maxWords);
            combos.forEach(words => {
                multiResults.push({ words, language: lang });
            });
        });

        singleResults.sort((a, b) => a.word.localeCompare(b.word));
        // Sortera kombinationer: färre ord först, sedan alfabetiskt
        multiResults.sort((a, b) => {
            if (a.words.length !== b.words.length) return a.words.length - b.words.length;
            return a.words.join(' ').localeCompare(b.words.join(' '));
        });

        displayResults(singleResults, multiResults);
    }, 10);
}

// Event listeners
document.getElementById('searchBtn').addEventListener('click', searchAnagrams);

document.getElementById('letterInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchAnagrams();
    }
});

// Sök igen när språkval ändras
document.querySelectorAll('input[name="language"]').forEach(checkbox => {
    checkbox.addEventListener('change', () => {
        const input = document.getElementById('letterInput').value;
        if (input.trim()) {
            searchAnagrams();
        }
    });
});

// Sök igen när långa kombinationer ändras
document.getElementById('longCombos').addEventListener('change', () => {
    const input = document.getElementById('letterInput').value;
    if (input.trim()) {
        searchAnagrams();
    }
});

// Initial meddelande
document.getElementById('results').innerHTML = '<p class="info-text">Skriv in bokstäver för att börja söka</p>';
