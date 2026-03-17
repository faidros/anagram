// Normalisera och sortera bokstäver för anagramjämförelse
function normalizeWord(word) {
    return word
        .toLowerCase()
        .replace(/[^a-zäöåæøëïéèêü]/g, '')
        .split('')
        .sort()
        .join('');
}

// Hitta anagram
function findAnagrams(letters, wordList) {
    const normalized = normalizeWord(letters);
    
    if (normalized.length === 0) {
        return [];
    }

    return wordList.filter(word => {
        // Ordet måste ha samma längd och samma bokstäver
        return normalizeWord(word) === normalized;
    });
}

// Hämta valda språk
function getSelectedLanguages() {
    const checkboxes = document.querySelectorAll('input[name="language"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// Visa resultaten
function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    
    if (results.length === 0) {
        resultsDiv.innerHTML = '<p class="no-results">Inga anagram funna. Försök med andra bokstäver!</p>';
        return;
    }

    // Gruppera resultaten efter språk
    const grouped = {};
    results.forEach(result => {
        if (!grouped[result.language]) {
            grouped[result.language] = [];
        }
        grouped[result.language].push(result.word);
    });

    let html = '<div class="results-grid">';
    
    results.forEach(result => {
        html += `
            <div class="result-word">
                ${result.word}
                <div class="result-language">${getLanguageName(result.language)}</div>
            </div>
        `;
    });

    html += '</div>';
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

    // Samla alla anagram från alla valda språk
    const allResults = [];

    selectedLanguages.forEach(lang => {
        const wordList = WORDLISTS[lang] || [];
        const anagrams = findAnagrams(input, wordList);
        
        anagrams.forEach(word => {
            allResults.push({
                word: word,
                language: lang
            });
        });
    });

    // Sortera resultaten alfabetiskt
    allResults.sort((a, b) => a.word.localeCompare(b.word));

    displayResults(allResults);
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

// Initial meddelande
document.getElementById('results').innerHTML = '<p class="info-text">Skriv in bokstäver för att börja söka</p>';
