# CaesarAI Cloud Run FastAPI Template



To run a lcoally:
```
./build_app.sh --local
```

To run a migration run.
```
./build_app.sh --migrate
```

To build to prod:
```
./build_app.sh --prod
```

## Regression Testing
1. To allow for regression testing 

```
nvm use v20.20.0
```
```
 npm install supabase --save-dev
 ```
 ```
npx supabase init
   ```