const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

class DatabaseManager {
  constructor() {
    this.db = null;
    this.init();
  }

  init() {
    // Ensure data directory exists
    const dataDir = path.join(__dirname, '../../data');
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }

    // Initialize database
    const dbPath = path.join(dataDir, 'bot.db');
    this.db = new Database(dbPath);
    
    // Create tables
    this.createTables();
  }

  createTables() {
    // Modlog table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS modlog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        moderator_id TEXT NOT NULL,
        action TEXT NOT NULL,
        reason TEXT,
        duration TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        case_id INTEGER
      )
    `);

    // Guild settings table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS guild_settings (
        guild_id TEXT PRIMARY KEY,
        modlog_channel_id TEXT,
        welcome_channel_id TEXT,
        prefix TEXT DEFAULT '!',
        automod_enabled INTEGER DEFAULT 0,
        antispam_enabled INTEGER DEFAULT 0,
        anticaps_enabled INTEGER DEFAULT 0,
        antilinks_enabled INTEGER DEFAULT 0,
        antiinvite_enabled INTEGER DEFAULT 0,
        wordfilter_enabled INTEGER DEFAULT 0,
        massmention_enabled INTEGER DEFAULT 0,
        antispam_threshold INTEGER DEFAULT 5,
        anticaps_threshold INTEGER DEFAULT 70,
        massmention_threshold INTEGER DEFAULT 5,
        antispam_action TEXT DEFAULT 'delete',
        anticaps_action TEXT DEFAULT 'delete',
        antilinks_action TEXT DEFAULT 'delete',
        antiinvite_action TEXT DEFAULT 'delete',
        wordfilter_action TEXT DEFAULT 'delete',
        massmention_action TEXT DEFAULT 'delete',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create indexes for better performance
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_modlog_guild_id ON modlog(guild_id);
      CREATE INDEX IF NOT EXISTS idx_modlog_user_id ON modlog(user_id);
      CREATE INDEX IF NOT EXISTS idx_modlog_timestamp ON modlog(timestamp);
    `);
  }

  // Add a modlog entry
  addModlogEntry(guildId, userId, moderatorId, action, reason = null, duration = null) {
    const stmt = this.db.prepare(`
      INSERT INTO modlog (guild_id, user_id, moderator_id, action, reason, duration, case_id)
      VALUES (?, ?, ?, ?, ?, ?, (SELECT COALESCE(MAX(case_id), 0) + 1 FROM modlog WHERE guild_id = ?))
    `);
    
    return stmt.run(guildId, userId, moderatorId, action, reason, duration, guildId);
  }

  // Get modlog entries for a user
  getUserModlog(guildId, userId, limit = 10) {
    const stmt = this.db.prepare(`
      SELECT * FROM modlog 
      WHERE guild_id = ? AND user_id = ? 
      ORDER BY timestamp DESC 
      LIMIT ?
    `);
    
    return stmt.all(guildId, userId, limit);
  }

  // Get all modlog entries for a guild
  getGuildModlog(guildId, limit = 50) {
    const stmt = this.db.prepare(`
      SELECT * FROM modlog 
      WHERE guild_id = ? 
      ORDER BY timestamp DESC 
      LIMIT ?
    `);
    
    return stmt.all(guildId, limit);
  }

  // Get a specific modlog entry by case ID
  getModlogCase(guildId, caseId) {
    const stmt = this.db.prepare(`
      SELECT * FROM modlog 
      WHERE guild_id = ? AND case_id = ?
    `);
    
    return stmt.get(guildId, caseId);
  }

  // Set guild settings
  setGuildSettings(guildId, settings) {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO guild_settings 
      (guild_id, modlog_channel_id, welcome_channel_id, prefix, 
       automod_enabled, antispam_enabled, anticaps_enabled, antilinks_enabled, 
       antiinvite_enabled, wordfilter_enabled, massmention_enabled,
       antispam_threshold, anticaps_threshold, massmention_threshold,
       antispam_action, anticaps_action, antilinks_action, antiinvite_action, 
       wordfilter_action, massmention_action, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    `);
    
    return stmt.run(
      guildId,
      settings.modlog_channel_id || null,
      settings.welcome_channel_id || null,
      settings.prefix || '!',
      settings.automod_enabled || 0,
      settings.antispam_enabled || 0,
      settings.anticaps_enabled || 0,
      settings.antilinks_enabled || 0,
      settings.antiinvite_enabled || 0,
      settings.wordfilter_enabled || 0,
      settings.massmention_enabled || 0,
      settings.antispam_threshold || 5,
      settings.anticaps_threshold || 70,
      settings.massmention_threshold || 5,
      settings.antispam_action || 'delete',
      settings.anticaps_action || 'delete',
      settings.antilinks_action || 'delete',
      settings.antiinvite_action || 'delete',
      settings.wordfilter_action || 'delete',
      settings.massmention_action || 'delete'
    );
  }

  // Get guild settings
  getGuildSettings(guildId) {
    const stmt = this.db.prepare(`
      SELECT * FROM guild_settings WHERE guild_id = ?
    `);
    
    return stmt.get(guildId);
  }

  // Delete modlog entries (for data cleanup)
  deleteModlogEntries(guildId, daysOld = 90) {
    const stmt = this.db.prepare(`
      DELETE FROM modlog 
      WHERE guild_id = ? AND timestamp < datetime('now', '-${daysOld} days')
    `);
    
    return stmt.run(guildId);
  }

  // Get statistics
  getModlogStats(guildId) {
    const stmt = this.db.prepare(`
      SELECT 
        action,
        COUNT(*) as count
      FROM modlog 
      WHERE guild_id = ? 
      GROUP BY action
    `);
    
    return stmt.all(guildId);
  }

  // Close database connection
  close() {
    if (this.db) {
      this.db.close();
    }
  }
}

module.exports = new DatabaseManager(); 