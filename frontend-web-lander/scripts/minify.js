const fs = require('fs');
const path = require('path');

console.log('🗜️  Minifying assets...');

// Simple minification functions (basic versions)
function minifyHTML(html) {
    return html
        .replace(/\s+/g, ' ')
        .replace(/>\s+</g, '><')
        .replace(/\s+>/g, '>')
        .replace(/<\s+/g, '<')
        .trim();
}

function minifyCSS(css) {
    return css
        .replace(/\/\*[\s\S]*?\*\//g, '')
        .replace(/\s+/g, ' ')
        .replace(/;\s*}/g, '}')
        .replace(/\s*{\s*/g, '{')
        .replace(/;\s*/g, ';')
        .replace(/,\s*/g, ',')
        .replace(/:\s*/g, ':')
        .trim();
}

function minifyJS(js) {
    return js
        .replace(/\/\*[\s\S]*?\*\//g, '')
        .replace(/\/\/.*$/gm, '')
        .replace(/\s+/g, ' ')
        .replace(/;\s*}/g, '}')
        .replace(/\s*{\s*/g, '{')
        .replace(/;\s*/g, ';')
        .replace(/,\s*/g, ',')
        .trim();
}

// Create minified versions directory
const minifiedDir = path.join(__dirname, '..', 'dist');
if (!fs.existsSync(minifiedDir)) {
    fs.mkdirSync(minifiedDir, { recursive: true });
}

// Minify HTML files
const htmlFiles = fs.readdirSync(__dirname + '/..')
    .filter(file => file.endsWith('.html'));

htmlFiles.forEach(file => {
    const filePath = path.join(__dirname, '..', file);
    const content = fs.readFileSync(filePath, 'utf8');
    const minified = minifyHTML(content);
    
    const outputPath = path.join(minifiedDir, file);
    fs.writeFileSync(outputPath, minified);
    
    const savings = ((content.length - minified.length) / content.length * 100).toFixed(1);
    console.log(`✅ Minified ${file} - Saved ${savings}% (${content.length - minified.length} bytes)`);
});

// Minify CSS files
const cssFiles = fs.readdirSync(__dirname + '/..')
    .filter(file => file.endsWith('.css'));

cssFiles.forEach(file => {
    const filePath = path.join(__dirname, '..', file);
    const content = fs.readFileSync(filePath, 'utf8');
    const minified = minifyCSS(content);
    
    const outputPath = path.join(minifiedDir, file);
    fs.writeFileSync(outputPath, minified);
    
    const savings = ((content.length - minified.length) / content.length * 100).toFixed(1);
    console.log(`✅ Minified ${file} - Saved ${savings}% (${content.length - minified.length} bytes)`);
});

// Minify JS files
const jsFiles = fs.readdirSync(__dirname + '/..')
    .filter(file => file.endsWith('.js') && !file.includes('node_modules') && file !== 'server.js');

jsFiles.forEach(file => {
    const filePath = path.join(__dirname, '..', file);
    const content = fs.readFileSync(filePath, 'utf8');
    const minified = minifyJS(content);
    
    const outputPath = path.join(minifiedDir, file);
    fs.writeFileSync(outputPath, minified);
    
    const savings = ((content.length - minified.length) / content.length * 100).toFixed(1);
    console.log(`✅ Minified ${file} - Saved ${savings}% (${content.length - minified.length} bytes)`);
});

// Copy server.js and package.json to dist
fs.copyFileSync(path.join(__dirname, '..', 'server.js'), path.join(minifiedDir, 'server.js'));
fs.copyFileSync(path.join(__dirname, '..', 'package.json'), path.join(minifiedDir, 'package.json'));

console.log('✨ Minification complete! Files saved to /dist directory');
console.log('📦 Ready for production deployment');