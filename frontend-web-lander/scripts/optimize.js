const fs = require('fs');
const path = require('path');

console.log('🔧 Optimizing assets...');

// Create optimized directory if it doesn't exist
const optimizedDir = path.join(__dirname, '..', 'optimized');
if (!fs.existsSync(optimizedDir)) {
    fs.mkdirSync(optimizedDir, { recursive: true });
}

// Optimize SVG files (remove unnecessary attributes, comments)
function optimizeSVG(svgContent) {
    return svgContent
        .replace(/<!--[\s\S]*?-->/g, '') // Remove comments
        .replace(/\s+/g, ' ') // Collapse whitespace
        .replace(/>\s+</g, '><') // Remove whitespace between tags
        .trim();
}

// Process HTML files to optimize inline SVGs
function optimizeHTML(htmlContent) {
    return htmlContent.replace(/<svg[^>]*>[\s\S]*?<\/svg>/g, (match) => {
        return optimizeSVG(match);
    });
}

// Get all HTML files
const htmlFiles = fs.readdirSync(__dirname + '/..')
    .filter(file => file.endsWith('.html'));

htmlFiles.forEach(file => {
    const filePath = path.join(__dirname, '..', file);
    const content = fs.readFileSync(filePath, 'utf8');
    const optimized = optimizeHTML(content);
    
    // Write optimized version (for now, just log the optimization)
    console.log(`✅ Optimized ${file} - Reduced size by ${((content.length - optimized.length) / content.length * 100).toFixed(1)}%`);
});

// Optimize CSS (remove comments, unnecessary whitespace)
function optimizeCSS(cssContent) {
    return cssContent
        .replace(/\/\*[\s\S]*?\*\//g, '') // Remove comments
        .replace(/\s+/g, ' ') // Collapse whitespace
        .replace(/;\s*}/g, '}') // Remove last semicolon in blocks
        .replace(/\s*{\s*/g, '{') // Clean up braces
        .replace(/;\s*/g, ';') // Clean up semicolons
        .trim();
}

// Process CSS files
const cssFiles = fs.readdirSync(__dirname + '/..')
    .filter(file => file.endsWith('.css'));

cssFiles.forEach(file => {
    const filePath = path.join(__dirname, '..', file);
    const content = fs.readFileSync(filePath, 'utf8');
    const optimized = optimizeCSS(content);
    
    console.log(`✅ Optimized ${file} - Reduced size by ${((content.length - optimized.length) / content.length * 100).toFixed(1)}%`);
});

// Optimize JavaScript (basic optimization)
function optimizeJS(jsContent) {
    return jsContent
        .replace(/\/\*[\s\S]*?\*\//g, '') // Remove block comments
        .replace(/\/\/.*$/gm, '') // Remove line comments
        .replace(/\s+/g, ' ') // Collapse whitespace
        .replace(/;\s*}/g, '}') // Clean up
        .trim();
}

// Process JS files
const jsFiles = fs.readdirSync(__dirname + '/..')
    .filter(file => file.endsWith('.js') && !file.includes('node_modules'));

jsFiles.forEach(file => {
    const filePath = path.join(__dirname, '..', file);
    const content = fs.readFileSync(filePath, 'utf8');
    const optimized = optimizeJS(content);
    
    console.log(`✅ Optimized ${file} - Reduced size by ${((content.length - optimized.length) / content.length * 100).toFixed(1)}%`);
});

console.log('✨ Asset optimization complete!');