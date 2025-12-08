# Adding Database to PgAdmin - Complete Guide

## Database Information

**Database Name:** `imdb_reddit`
**Status:** ✅ EXISTS in PostgreSQL
**Contains:** 77 films, 308 actors, 62 rated actors

---

## Step-by-Step Instructions

### Step 1: Access PgAdmin
Open your browser and go to:
```
http://localhost:5050/
```

### Step 2: Login
Use these credentials:
```
Email:    admin@admin.com
Password: admin
```

### Step 3: Register a New Server

In the PgAdmin interface:

1. **Left Sidebar:** Right-click on **"Servers"**
2. Select **"Register"** → **"Server..."**

### Step 4: Fill Server Details

#### General Tab:
- **Name:** `imdb_reddit` (you can name it anything)
- **Description:** (optional) `Actor Rating Database`

#### Connection Tab:
- **Host name/address:** `postgres`
- **Port:** `5432`
- **Maintenance database:** (leave empty)
- **Username:** `postgres`
- **Password:** `postgres`
- **Save password?** ✅ Check this box

#### Advanced Tab:
- Leave all defaults

### Step 5: Click Save

The server should now appear in your Servers list.

---

## Alternative Connection Methods

If the above doesn't work, try one of these:

### Option 1: Using Container Name
```
Host:     imdb_postgres
Port:     5432
Username: postgres
Password: postgres
```

### Option 2: Using Docker Network IP
```
Host:     172.18.0.2
Port:     5432
Username: postgres
Password: postgres
```

### Option 3: Using Localhost
```
Host:     localhost
Port:     5432
Username: postgres
Password: postgres
```

---

## Expected Result

After adding the server, you should see:

```
Servers
└── postgres (or imdb_reddit)
    ├── Databases
    │   ├── imdb_reddit ✅
    │   ├── postgres
    │   ├── template0
    │   └── template1
    ├── Login/Group Roles
    └── Tablespaces
```

### Inside imdb_reddit Database:
```
imdb_reddit
├── Schemas
│   └── public
│       ├── Tables
│       │   ├── films (77 rows)
│       │   ├── actors (308 rows)
│       │   └── actor_ratings (62 rows)
│       └── [Other Airflow tables]
└── [Other objects]
```

---

## Verify Connection

You can run these queries in PgAdmin to verify:

1. **Count Films:**
```sql
SELECT COUNT(*) as films FROM films;
```
Expected result: `77`

2. **Count Actors:**
```sql
SELECT COUNT(*) as actors FROM actors;
```
Expected result: `308`

3. **Count Rated Actors:**
```sql
SELECT COUNT(*) as rated_actors FROM actor_ratings;
```
Expected result: `62`

4. **View Top Actors:**
```sql
SELECT * FROM actor_ratings ORDER BY average_rating DESC LIMIT 10;
```

---

## Troubleshooting

### Issue: "Cannot connect to server"

**Solution 1:** Check if PostgreSQL is running
```bash
docker ps | grep postgres
```

**Solution 2:** Check PostgreSQL logs
```bash
docker logs imdb_postgres
```

**Solution 3:** Test connection directly
```bash
docker exec imdb_postgres psql -U postgres -d imdb_reddit -c "SELECT COUNT(*) FROM films;"
```

### Issue: "Authentication failed"

Make sure you're using:
- **Username:** `postgres` (NOT `admin`)
- **Password:** `postgres`
- **Database:** `imdb_reddit`

### Issue: "Host not found"

Try these hosts in order:
1. `postgres` (Docker network name)
2. `imdb_postgres` (Container name)
3. `localhost` (Direct connection)
4. `172.18.0.2` (Docker network IP)

### Issue: Port already in use

Check if PostgreSQL is running:
```bash
docker port imdb_postgres
```

Should show: `5432/tcp -> 0.0.0.0:5432`

---

## Quick Verification

To confirm everything is working, run this in PowerShell:

```powershell
docker exec imdb_postgres psql -U postgres -d imdb_reddit -c "SELECT 'Connection OK' as status, COUNT(*) as films FROM films;"
```

You should see:
```
 status      | films
─────────────┼───────
 Connection OK |   77
```

---

## If Still Not Working

Try this complete troubleshooting checklist:

1. ✅ PostgreSQL container running?
   ```bash
   docker ps | grep postgres
   ```

2. ✅ PgAdmin container running?
   ```bash
   docker ps | grep pgadmin
   ```

3. ✅ PostgreSQL healthy?
   ```bash
   docker logs imdb_postgres
   ```

4. ✅ Database exists?
   ```bash
   docker exec imdb_postgres psql -U postgres -l
   ```

5. ✅ Can connect directly?
   ```bash
   docker exec imdb_postgres psql -U postgres -d imdb_reddit -c "\dt"
   ```

If all show ✅, then your database and PostgreSQL are working fine. The issue is just the PgAdmin connection configuration.

---

## Need Help?

**Check logs:**
```bash
docker logs imdb_pgadmin
```

**Restart services:**
```bash
docker-compose -f docker/docker-compose.yml restart
```

**Reset everything:**
```bash
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d
```

---

**Last Updated:** December 8, 2025
**Database Status:** ✅ OPERATIONAL
