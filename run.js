#!/usr/bin/env node

const { spawn } = require('child_process');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('🤖 Discord Bot Launcher');
console.log('========================');
console.log('');
console.log('Choose how to run your bot:');
console.log('1. Normal mode (single process)');
console.log('2. Sharded mode (multiple shards)');
console.log('3. Clustered mode (multiple processes)');
console.log('4. Development mode (with auto-restart)');
console.log('5. Deploy commands only');
console.log('');

rl.question('Enter your choice (1-5): ', (choice) => {
  let command;
  let description;

  switch (choice.trim()) {
    case '1':
      command = 'npm start';
      description = 'Starting bot in normal mode...';
      break;
    case '2':
      command = 'npm run shard';
      description = 'Starting bot with sharding...';
      break;
    case '3':
      command = 'npm run cluster';
      description = 'Starting bot with clustering...';
      break;
    case '4':
      command = 'npm run dev';
      description = 'Starting bot in development mode...';
      break;
    case '5':
      command = 'npm run deploy';
      description = 'Deploying slash commands...';
      break;
    default:
      console.log('❌ Invalid choice. Please run the script again.');
      rl.close();
      return;
  }

  console.log(`\n${description}`);
  console.log('Press Ctrl+C to stop the bot\n');

  const child = spawn(command, [], {
    stdio: 'inherit',
    shell: true
  });

  child.on('error', (error) => {
    console.error('❌ Error starting bot:', error.message);
    rl.close();
  });

  child.on('close', (code) => {
    console.log(`\n✅ Bot process exited with code ${code}`);
    rl.close();
  });

  // Handle process termination
  process.on('SIGINT', () => {
    console.log('\n🛑 Stopping bot...');
    child.kill('SIGINT');
  });

  process.on('SIGTERM', () => {
    console.log('\n🛑 Stopping bot...');
    child.kill('SIGTERM');
  });
}); 