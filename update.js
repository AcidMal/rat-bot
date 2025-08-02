#!/usr/bin/env node

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('🔄 Discord Bot Updater');
console.log('======================');
console.log('');

// Check if we're in a git repository
if (!fs.existsSync('.git')) {
  console.log('❌ This directory is not a git repository.');
  console.log('Please run this script from your bot directory.');
  process.exit(1);
}

// Check if git is installed
try {
  execSync('git --version', { stdio: 'ignore' });
} catch (error) {
  console.log('❌ Git is not installed. Please install git first.');
  process.exit(1);
}

// Check if npm is installed
try {
  execSync('npm --version', { stdio: 'ignore' });
} catch (error) {
  console.log('❌ npm is not installed. Please install Node.js first.');
  process.exit(1);
}

async function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

async function runCommand(command, options = {}) {
  try {
    const result = execSync(command, { 
      encoding: 'utf8', 
      stdio: options.silent ? 'ignore' : 'inherit',
      ...options 
    });
    return { success: true, output: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

async function main() {
  console.log('📦 Checking for updates...');

  // Get current branch
  const branchResult = await runCommand('git branch --show-current', { silent: true });
  if (!branchResult.success) {
    console.log('❌ Failed to get current branch.');
    process.exit(1);
  }
  const currentBranch = branchResult.output.trim();
  console.log(`📍 Current branch: ${currentBranch}`);

  // Fetch latest changes
  console.log('📥 Fetching latest changes from remote...');
  const fetchResult = await runCommand('git fetch origin');
  if (!fetchResult.success) {
    console.log('❌ Failed to fetch from remote.');
    process.exit(1);
  }

  // Check if there are any updates
  const localCommitResult = await runCommand('git rev-parse HEAD', { silent: true });
  const remoteCommitResult = await runCommand(`git rev-parse origin/${currentBranch}`, { silent: true });
  
  if (!localCommitResult.success || !remoteCommitResult.success) {
    console.log('❌ Failed to get commit information.');
    process.exit(1);
  }

  const localCommit = localCommitResult.output.trim();
  const remoteCommit = remoteCommitResult.output.trim();

  if (localCommit === remoteCommit) {
    console.log('✅ Bot is already up to date!');
    console.log('');
    
    const updateDeps = await question('Would you like to update dependencies anyway? (y/N): ');
    if (updateDeps.toLowerCase() === 'y') {
      console.log('📦 Updating dependencies...');
      await runCommand('npm update');
      console.log('✅ Dependencies updated!');
    } else {
      console.log('🔄 No updates needed.');
      rl.close();
      return;
    }
  } else {
    console.log('🔄 Updates found! Pulling latest changes...');
    
    // Check for uncommitted changes
    const statusResult = await runCommand('git status --porcelain', { silent: true });
    const hasChanges = statusResult.success && statusResult.output.trim() !== '';
    
    if (hasChanges) {
      console.log('⚠️  Warning: You have uncommitted changes.');
      console.log('Your changes will be stashed before pulling.');
      const continueUpdate = await question('Continue? (y/N): ');
      if (continueUpdate.toLowerCase() !== 'y') {
        console.log('❌ Update cancelled.');
        rl.close();
        return;
      }
      
      // Stash changes
      console.log('📦 Stashing local changes...');
      await runCommand(`git stash push -m "Auto-stash before update ${new Date().toISOString()}"`);
    }
    
    // Pull latest changes
    console.log('📥 Pulling latest changes...');
    const pullResult = await runCommand(`git pull origin ${currentBranch}`);
    
    if (pullResult.success) {
      console.log('✅ Successfully pulled latest changes!');
      
      // Update dependencies
      console.log('📦 Updating dependencies...');
      await runCommand('npm update');
      
      // Install any new dependencies
      console.log('📦 Installing any new dependencies...');
      await runCommand('npm install');
      
      console.log('✅ Bot updated successfully!');
      
      // Show recent commits
      console.log('');
      console.log('📝 Recent changes:');
      await runCommand('git log --oneline -5');
      
      // Restore stashed changes if any
      const stashListResult = await runCommand('git stash list', { silent: true });
      if (stashListResult.success && stashListResult.output.includes('Auto-stash before update')) {
        console.log('');
        console.log('📦 Restoring your local changes...');
        const stashPopResult = await runCommand('git stash pop');
        if (stashPopResult.success) {
          console.log('✅ Local changes restored!');
        } else {
          console.log('⚠️  Warning: Could not automatically restore local changes.');
          console.log('You can restore them manually with: git stash pop');
        }
      }
      
    } else {
      console.log('❌ Failed to pull latest changes.');
      console.log('Please check your internet connection and try again.');
      process.exit(1);
    }
  }

  // Check for any new environment variables
  console.log('');
  console.log('🔧 Checking for new environment variables...');
  if (fs.existsSync('env.example')) {
    if (fs.existsSync('.env')) {
      console.log('✅ Environment variables file exists.');
      console.log('Please manually check env.example for any new variables.');
    } else {
      console.log('⚠️  No .env file found. Please create one based on env.example');
    }
  }

  // Check for any new scripts
  console.log('');
  console.log('🔧 Checking for new scripts...');
  if (fs.existsSync('package.json')) {
    console.log('Available npm scripts:');
    const scriptsResult = await runCommand('npm run', { silent: true });
    if (scriptsResult.success) {
      const lines = scriptsResult.output.split('\n');
      lines.forEach(line => {
        if (line.match(/^  [a-z-]+$/)) {
          console.log(`  npm run ${line.trim()}`);
        }
      });
    }
  }

  // Final status
  console.log('');
  console.log('🎉 Update completed!');
  console.log('');
  console.log('Next steps:');
  console.log('1. Review any new environment variables and update your .env file');
  console.log('2. Test your bot: npm start');
  console.log('3. Deploy any new commands: npm run deploy');
  console.log('');
  console.log('If you encounter any issues, check the logs and ensure all dependencies are properly installed.');

  rl.close();
}

main().catch(error => {
  console.error('❌ An error occurred:', error.message);
  rl.close();
  process.exit(1);
}); 