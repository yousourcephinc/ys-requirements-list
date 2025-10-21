#!/usr/bin/env python3
"""
Test client for the Guides REST API.

This script demonstrates how to use the Guides REST API.

Usage:
  python test_guides_api.py [base_url]
"""

import sys
import requests
import json

def test_guides_api(base_url="http://localhost:8080"):
    """Test the Guides API functionality."""
    
    print(f"\n🚀 Testing Guides API at {base_url}")
    print("="*60)
    
    # Test 1: Get API info
    print("\n📋 Getting API info...")
    response = requests.get(f"{base_url}/")
    if response.status_code == 200:
        info = response.json()
        print(f"✅ Service: {info['service']} v{info['version']}")
        print(f"   Description: {info['description']}")
    else:
        print(f"❌ Failed to get API info: {response.status_code}")
        return
    
    # Test 2: List divisions
    print("\n📂 Testing /divisions...")
    response = requests.get(f"{base_url}/divisions")
    if response.status_code == 200:
        divisions = response.json()
        print(f"✅ Found {len(divisions)} divisions:")
        for div in divisions[:5]:
            print(f"   - {div['name']} ({div['guide_count']} guides)")
        
        if not divisions:
            print("⚠️  No divisions found. Make sure guides directory exists and has been populated.")
            return
            
        # Test 3: List guides in first division
        test_division = divisions[0]["name"]
        print(f"\n📚 Testing /divisions/{test_division}/guides...")
        response = requests.get(f"{base_url}/divisions/{test_division}/guides")
        if response.status_code == 200:
            guides = response.json()
            print(f"✅ Found {len(guides)} guides in '{test_division}':")
            for i, guide in enumerate(guides[:3], 1):
                print(f"   {i}. {guide['title']} (Maturity: {guide['maturity']})")
            
            if guides:
                # Test 4: Get guide content
                test_guide_path = guides[0]["path"]
                print(f"\n📄 Testing /guides/{test_guide_path}...")
                response = requests.get(f"{base_url}/guides/{test_guide_path}")
                if response.status_code == 200:
                    guide = response.json()
                    print(f"✅ Guide: {guide['title']}")
                    print(f"   Division: {guide['division']}")
                    print(f"   Maturity: {guide['maturity']}")
                    print(f"   Content preview: {guide['content'][:100]}...")
                else:
                    print(f"❌ Failed to get guide content: {response.status_code}")
        else:
            print(f"❌ Failed to list guides: {response.status_code}")
    else:
        print(f"❌ Failed to list divisions: {response.status_code}")
        return
    
    # Test 5: Search guides
    print("\n🔍 Testing /search...")
    response = requests.post(
        f"{base_url}/search",
        json={"query": "authentication", "top_k": 3}
    )
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Found {len(results)} results for 'authentication':")
        for i, result in enumerate(results, 1):
            print(f"\n   {i}. {result['title']} ({result['division']})")
            print(f"      Score: {result['score']:.3f}")
            print(f"      Path: {result['file_path']}")
    else:
        print(f"❌ Search failed: {response.status_code}")
    
    # Test 6: Get recommendations
    print("\n👉 Testing /recommendations...")
    response = requests.post(
        f"{base_url}/recommendations",
        json={"topics": ["authentication", "security"]}
    )
    if response.status_code == 200:
        recommendations = response.json()
        print(f"✅ Found {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n   {i}. {rec['title']} ({rec['division']})")
            print(f"      Score: {rec['score']:.3f}")
    else:
        print(f"❌ Recommendations failed: {response.status_code}")
    
    print("\n✅ All tests completed!")
    print("="*60)


if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    try:
        test_guides_api(base_url)
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {base_url}")
        print("   Make sure the API server is running.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
