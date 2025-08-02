#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔍 Discord Bot Diagnostic Test');
console.log('==============================');
console.log('');

// Check Node.js version
console.log('📋 System Information:');
console.log(`   Node.js version: ${process.version}`);
console.log(`   Current directory: ${process.cwd()}`);
console.log(`   Platform: ${process.platform}`);
console.log('');

// Check if .env file exists
console.log('🔧 Environment Check:');
if (fs.existsSync('.env')) {
  console.log('   ✅ .env file found');
  
  // Load and check environment variables
  require('dotenv').config();
  
  if (process.env.DISCORD_TOKEN) {
    console.log('   ✅ DISCORD_TOKEN found');
    console.log(`   📝 Token starts with: ${process.env.DISCORD_TOKEN.substring(0, 10)}...`);
  } else {
    console.log('   ❌ DISCORD_TOKEN not found in .env file');
  }
  
  if (process.env.CLIENT_ID) {
    console.log('   ✅ CLIENT_ID found');
  } else {
    console.log('   ❌ CLIENT_ID not found in .env file');
  }
  
  if (process.env.GUILD_ID) {
    console.log('   ✅ GUILD_ID found');
  } else {
    console.log('   ❌ GUILD_ID not found in .env file');
  }
} else {
  console.log('   ❌ .env file not found');
}
console.log('');

// Check if package.json exists
console.log('📦 Package Check:');
if (fs.existsSync('package.json')) {
  console.log('   ✅ package.json found');
  
  try {
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    console.log(`   📝 Project name: ${packageJson.name}`);
    console.log(`   📝 Version: ${packageJson.version}`);
    
    if (packageJson.dependencies) {
      console.log('   📋 Dependencies:');
      Object.keys(packageJson.dependencies).forEach(dep => {
        console.log(`      - ${dep}: ${packageJson.dependencies[dep]}`);
      });
    }
  } catch (error) {
    console.log('   ❌ Error reading package.json:', error.message);
  }
} else {
  console.log('   ❌ package.json not found');
}
console.log('');

// Check if src directory exists
console.log('📁 Directory Structure Check:');
const srcPath = path.join(__dirname, 'src');
if (fs.existsSync(srcPath)) {
  console.log('   ✅ src directory found');
  
  // Check subdirectories
  const subdirs = ['commands', 'events', 'utils'];
  subdirs.forEach(subdir => {
    const subdirPath = path.join(srcPath, subdir);
    if (fs.existsSync(subdirPath)) {
      const files = fs.readdirSync(subdirPath).filter(f => f.endsWith('.js'));
      console.log(`   ✅ ${subdir} directory found (${files.length} .js files)`);
    } else {
      console.log(`   ❌ ${subdir} directory not found`);
    }
  });
} else {
  console.log('   ❌ src directory not found');
}
console.log('');

// Check if node_modules exists
console.log('📦 Dependencies Check:');
if (fs.existsSync('node_modules')) {
  console.log('   ✅ node_modules directory found');
  
  // Check key dependencies
  const keyDeps = ['discord.js', 'dotenv', '@discordjs/voice'];
  keyDeps.forEach(dep => {
    const depPath = path.join('node_modules', dep);
    if (fs.existsSync(depPath)) {
      console.log(`   ✅ ${dep} installed`);
    } else {
      console.log(`   ❌ ${dep} not installed`);
    }
  });
} else {
  console.log('   ❌ node_modules directory not found');
  console.log('   💡 Run: npm install');
}
console.log('');

// Test Discord.js import
console.log('🔌 Discord.js Test:');
try {
  const { Client, GatewayIntentBits } = require('discord.js');
  console.log('   ✅ Discord.js imported successfully');
  
  // Test client creation
  const client = new Client({
    intents: [GatewayIntentBits.Guilds]
  });
  console.log('   ✅ Discord.js client created successfully');
} catch (error) {
  console.log('   ❌ Discord.js import failed:', error.message);
}
console.log('');

console.log('🎯 Recommendations:');
console.log('   1. Make sure all required files exist');
console.log('   2. Check that .env file has correct values');
console.log('   3. Run: npm install (if node_modules missing)');
console.log('   4. Try running: node src/index.js');
console.log('');

console.log('✅ Diagnostic test completed!'); 