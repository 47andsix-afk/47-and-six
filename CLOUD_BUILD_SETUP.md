# Google Cloud Build Setup (Web Console)

## Step 1: Create/Select Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click the **Project Selector** (top-left dropdown)
3. Click **NEW PROJECT**
4. Enter: `47andsix-concierge`
5. Click **CREATE**
6. **Copy your Project ID** (format: `something-12345`) - you'll need this

---

## Step 2: Enable Required APIs

1. Go to: https://console.cloud.google.com/apis/dashboard
2. Click **+ ENABLE APIS AND SERVICES**
3. Search for and enable these **one-by-one**:
   - **Cloud Build API**
   - **Cloud Source Repositories API**
   - **Service Networking API**

---

## Step 3: Set Up Cloud Source Repository

1. Go to: https://console.cloud.google.com/repos
2. Click **Create Repository**
3. Name: `ronin-concierge`
4. Select your project
5. Click **Create**

---

## Step 4: Connect Your Git Repository

You have **two options**:

### **Option A: Push from Local (Recommended)**

```powershell
# Install Google Cloud SDK
# Download from: https://cloud.google.com/sdk/docs/install

# Then in PowerShell:
gcloud init
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Go to your workspace
cd D:\workspace\repos\workspace

# Add Cloud Source as remote
git remote add google \
  https://source.developers.google.com/p/YOUR_PROJECT_ID/r/ronin-concierge

# Push your code
git push google main
```

### **Option B: GitHub Integration (If you use GitHub)**

1. Go to: https://console.cloud.google.com/cloud-build/repositories
2. Click **Connect Repository**
3. Select **GitHub**
4. Authorize GitHub access
5. Select your repo
6. Click **Connect**

---

## Step 5: Create Cloud Build Trigger

1. Go to: https://console.cloud.google.com/cloud-build/triggers
2. Click **Create Trigger**
3. Fill in:
   - **Name**: `ronin-agents-test`
   - **Repository**: Select `ronin-concierge` (or your GitHub repo)
   - **Branch pattern**: `^main$`
   - **Build configuration**: `cloudbuild.yaml`
4. Click **Create**

---

## Step 6: Test the Build

1. Make a commit to your main branch:
   ```powershell
   cd D:\workspace\repos\workspace
   git add .
   git commit -m "test: verify cloud build trigger"
   git push google main  # or 'git push origin main' for GitHub
   ```

2. Go to: https://console.cloud.google.com/cloud-build/builds
3. Watch your build run!

---

## Step 7: View Build Results

- **Successful build**: Green checkmark ✅
- **Failed build**: Red X ❌
- **Click any build** to see:
  - Test results
  - Logs
  - Artifacts

---

## Troubleshooting

### Build fails with "permission denied"
- Go to: https://console.cloud.google.com/iam-admin/iam
- Find: `YOUR_PROJECT_ID@cloudbuild.gserviceaccount.com`
- Grant role: **Cloud Build Service Account**

### Repository not syncing
- Check: https://console.cloud.google.com/cloud-build/repositories
- Click **Reconnect** if needed

### Tests not running
- Verify `cloudbuild.yaml` exists in repo root
- Check Python version matches (3.11)
- View build logs for errors

---

## Next Steps

Once builds are working:
1. **Add deployment step** to `cloudbuild.yaml` (Cloud Run, Compute Engine, etc.)
2. **Set up notifications** (Slack, email, webhooks)
3. **Configure environment secrets** (GEMINI_API_KEY)

Need help with any step?
