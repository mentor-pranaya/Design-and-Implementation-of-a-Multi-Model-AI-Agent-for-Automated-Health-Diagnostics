#!/bin/bash
# 🚀 Quick performance test commands for INBLOODO AGENT

API_KEY="your-api-key"
BASE_URL="http://localhost:10000"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     ⚡ INBLOODO AGENT - Performance Test Suite ⚡         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Sample blood report data
BLOOD_DATA='{
  "hemoglobin": 14.5,
  "hematocrit": 42.3,
  "rbc": 4.8,
  "wbc": 7.2,
  "neutrophils": 65,
  "lymphocytes": 25,
  "platelets": 250,
  "glucose": 95,
  "creatinine": 0.9,
  "bun": 18,
  "sodium": 138,
  "potassium": 4.2,
  "chloride": 102,
  "co2": 24
}'

# Test 1: Health Check
echo "🔍 Test 1: Health Check (verify server running)"
echo "Command: curl $BASE_URL/health"
echo ""
curl -s "$BASE_URL/health" | jq . 2>/dev/null || curl -s "$BASE_URL/health"
echo ""
echo ""

# Test 2: First Request (builds cache)
echo "🔄 Test 2: First Analysis (builds cache, should be ~2-5s)"
echo "Command: curl -X POST '$BASE_URL/analyze-report/' ..."
echo ""
START=$(date +%s%N)
RESPONSE=$(curl -s -X POST "$BASE_URL/analyze-report/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$BLOOD_DATA")
END=$(date +%s%N)
ELAPSED=$(( (END - START) / 1000000 ))
echo "Response Time: ${ELAPSED}ms"
echo "$RESPONSE" | jq '.status, .from_cache, .processing_time' 2>/dev/null || echo "$RESPONSE" | grep -E "status|from_cache|processing_time"
echo ""
echo ""

# Test 3: Cached Request (instant!)
echo "⚡ Test 3: Cached Request (same data, should be <100ms!)"
echo "Command: curl -X POST '$BASE_URL/analyze-report/' (identical data)"
echo ""
START=$(date +%s%N)
RESPONSE=$(curl -s -X POST "$BASE_URL/analyze-report/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$BLOOD_DATA")
END=$(date +%s%N)
ELAPSED=$(( (END - START) / 1000000 ))
echo "Response Time: ${ELAPSED}ms ⚡"
echo "$RESPONSE" | jq '.status, .from_cache, .processing_time' 2>/dev/null || echo "$RESPONSE" | grep -E "status|from_cache|processing_time"
echo ""
echo ""

# Test 4: Performance Metrics
echo "📊 Test 4: Performance Metrics"
echo "Command: curl $BASE_URL/api/status"
echo ""
curl -s "$BASE_URL/api/status" | jq '.performance' 2>/dev/null || curl -s "$BASE_URL/api/status" | grep -A 20 "performance"
echo ""
echo ""

# Test 5: Batch Test (5 identical requests)
echo "🔁 Test 5: Batch Test (5 identical requests)"
echo ""
for i in {1..5}; do
  START=$(date +%s%N)
  curl -s -X POST "$BASE_URL/analyze-report/" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$BLOOD_DATA" > /dev/null 2>&1
  END=$(date +%s%N)
  ELAPSED=$(( (END - START) / 1000000 ))
  echo "  Request $i: ${ELAPSED}ms"
done
echo ""
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ✅ TESTS COMPLETE ✅                   ║"
echo "║                                                            ║"
echo "║  What You Should See:                                     ║"
echo "║  ✓ Test 1: Server status 'healthy'                       ║"
echo "║  ✓ Test 2: from_cache = false, ~2-5s                    ║"
echo "║  ✓ Test 3: from_cache = true, <100ms ⚡                 ║"
echo "║  ✓ Test 4: Positive hit rate in cache_stats             ║"
echo "║  ✓ Test 5: Progressive speedup, all <100ms ⚡           ║"
echo "║                                                            ║"
echo "║  Expected Speed Improvement: 20-100x! 🚀                ║"
echo "╚════════════════════════════════════════════════════════════╝"
