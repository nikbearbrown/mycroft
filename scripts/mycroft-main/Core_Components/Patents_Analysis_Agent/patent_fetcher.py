"""
Patent Intelligence System - Data Fetcher
Advanced patent data fetching from PatentSearch API.

Author: Darshan Rahul Rajopadhye
License: MIT
"""


import os
import sys
import json
import time
import argparse
import requests
import pandas as pd
from urllib.parse import urlencode


def fetch_patents_page(base_url, endpoint, api_key, query_params, size=1000, after=None):
    """Fetch a single page of patents using cursor pagination."""
    
    # Build parameters using cursor pagination (size + after)
    params = {
        "f": query_params.get("f", ["patent_id", "patent_title", "patent_date", "inventors"]),
        "q": query_params.get("q", {"patent_year": "2021"}),
        "s": [{"patent_id": "asc"}],  # Sort is required for cursor pagination
    }
    
    # Add pagination options
    if after:
        params["o"] = {"size": size, "after": after}
    else:
        params["o"] = {"size": size}
    
    # Build URL with parameters as JSON strings (like the working example)
    query_string = "&".join([f"{param_name}={json.dumps(param_val)}" for param_name, param_val in params.items()])
    url = f"{base_url}/{endpoint.strip('/')}/?{query_string}"
    
    print(f"Fetching (after={after}): {url[:150]}...")
    
    response = requests.get(url, headers={"X-Api-Key": api_key})
    
    if response.status_code != 200:
        print(f"❌ HTTP {response.status_code}: {response.text}")
        return None, None, None
    
    json_response = response.json()
    
    # Debug: print response keys on first page
    if after is None:
        print(f"📋 Response keys: {list(json_response.keys())}")
        if 'total_hits' in json_response:
            print(f"📊 Total available: {json_response['total_hits']}")
    
    # Get the data and the last record for next cursor
    data_key = None
    for key in json_response.keys():
        if key not in ['error', 'count', 'total_hits']:
            data_key = key
            break
    
    if not data_key:
        return None, None, None
        
    data = json_response.get(data_key, [])
    last_cursor = None
    
    if data:
        # Get the last patent_id for cursor pagination
        last_cursor = data[-1].get('patent_id')
        
    return json_response, data, last_cursor


def fetch_all_patents(base_url, endpoint, api_key, query_params, max_retries=5, sleep_time=2, checkpoint_file="patents.csv", checkpoint_interval=10):
    """Fetch all patents with pagination and checkpointing."""
    
    special_keys = {
        "api/v1/ipc": "ipcr", 
        "api/v1/wipo": "wipo",
    }
    
    def response_key(endpoint: str) -> str:
        """Get the response key from endpoint."""
        endpoint = endpoint.rstrip("/")
        leaf = endpoint.split("/")[-1]
        if leaf in special_keys:
            return special_keys[leaf]
        elif leaf.endswith("s"):
            return leaf + "es" 
        else:
            return leaf + "s"
    
    all_results = []
    cursor = None  # Start with no cursor (first page)
    page_num = 1
    total_records = None
    data_key = None
    
    # Load existing checkpoint if exists
    if os.path.exists(checkpoint_file):
        try:
            existing_df = pd.read_csv(checkpoint_file)
            all_results = existing_df.to_dict('records')
            if all_results:
                # Use the last patent_id as cursor to resume
                cursor = all_results[-1].get('patent_id')
            print(f"💾 Resuming from checkpoint: {len(all_results)} records, cursor={cursor}")
        except Exception as e:
            print(f"⚠️ Could not load checkpoint: {e}")
    
    while True:
        retries = 0
        response_data = None
        data = None
        next_cursor = None
        
        # Retry logic
        while retries < max_retries:
            try:
                response_data, data, next_cursor = fetch_patents_page(base_url, endpoint, api_key, query_params, 1000, cursor)
                if response_data is not None:
                    break
                retries += 1
                if retries < max_retries:
                    wait = sleep_time * (2 ** retries)
                    print(f"⚠️ Retrying in {wait}s... (attempt {retries + 1})")
                    time.sleep(wait)
            except Exception as e:
                print(f"⚠️ Request error: {e}")
                retries += 1
                if retries < max_retries:
                    wait = sleep_time * (2 ** retries)
                    print(f"⚠️ Retrying in {wait}s... (attempt {retries + 1})")
                    time.sleep(wait)
        
        if response_data is None or not data:
            if response_data is None:
                print(f"❌ Failed after {max_retries} retries. Saving progress and exiting.")
            else:
                print("✅ No more results available.")
            break
            
        # Get total count on first successful request
        if total_records is None and 'total_hits' in response_data:
            total_records = response_data['total_hits']
            print(f"📊 Total records available: {total_records}")
        
        # Debug: Show date range of current batch
        if data and 'patent_date' in data[0]:
            dates = [item.get('patent_date', 'N/A') for item in data if item.get('patent_date')]
            if dates:
                print(f"📅 Current batch date range: {min(dates)} to {max(dates)}")
        
        all_results.extend(data)
        print(f"✅ Page {page_num} fetched ({len(data)} records), total so far: {len(all_results)}")
        
        # Check if we have all records
        if total_records and len(all_results) >= total_records:
            print(f"✅ All {total_records} records fetched!")
            break
        
        # If we got fewer records than requested, we might be at the end
        if len(data) < 1000:
            print(f"📄 Received {len(data)} records (less than 1000) - might be at end")
        
        # No more data if cursor didn't change
        if not next_cursor or cursor == next_cursor:
            print("✅ Reached end of results (no new cursor)")
            break
            
        # Save checkpoint periodically
        if page_num % checkpoint_interval == 0:
            pd.DataFrame(all_results).to_csv(checkpoint_file, index=False)
            print(f"💾 Checkpoint saved at {checkpoint_file} (page {page_num})")
        
        # Update cursor for next iteration
        cursor = next_cursor
        page_num += 1
        
        # Small delay to be nice to the API
        time.sleep(0.1)
    
    # Final save
    if all_results:
        final_df = pd.DataFrame(all_results)
        final_df.to_csv(checkpoint_file, index=False)
        print(f"📂 Final results saved to {checkpoint_file} ({len(all_results)} records)")
        return final_df
    
    return pd.DataFrame()


def get_last_run_date(output_file):
    """Get the date of the last successful run."""
    last_run_file = output_file.replace('.csv', '_last_run.txt')
    if os.path.exists(last_run_file):
        try:
            with open(last_run_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            print(f"⚠️ Could not read last run date: {e}")
    return None


def main():
    parser = argparse.ArgumentParser(description="Fetch patent data from PatentsView API")
    parser.add_argument("--base_url", default=os.getenv("PATENT_API_BASE", "https://search.patentsview.org"))
    parser.add_argument("--endpoint", default=os.getenv("PATENT_API_ENDPOINT", "api/v1/patent"))
    parser.add_argument("--api_key", default=os.getenv("PATENT_API_KEY", "xM1ScdAa.06Lz8WKH2U5FLdiqXbRtPIygexgeNP3L"))
    parser.add_argument("--year", default=os.getenv("PATENT_YEAR", "2024"), help="Patent year to fetch")
    parser.add_argument("--start_date", default=os.getenv("PATENT_START_DATE", ""), help="Start date (YYYY-MM-DD) - overrides year")
    parser.add_argument("--end_date", default=os.getenv("PATENT_END_DATE", ""), help="End date (YYYY-MM-DD) - requires start_date")
    parser.add_argument("--days_back", type=int, default=os.getenv("PATENT_DAYS_BACK", ""), help="Fetch patents from N days ago to today")
    parser.add_argument("--since_last_run", action="store_true", help="Fetch patents since last successful run")
    parser.add_argument("--output", default=os.getenv("PATENT_OUTPUT", "patents.csv"))
    parser.add_argument("--checkpoint_interval", type=int, default=5)
    args = parser.parse_args()
    
    if not args.api_key:
        print("❌ Error: API key required. Set PATENT_API_KEY environment variable or use --api_key")
        sys.exit(1)
    
    # Build date filter query
    query_filter = {}
    
    if args.since_last_run:
        # Fetch patents since last successful run
        last_run_date = get_last_run_date(args.output)
        if last_run_date:
            from datetime import datetime
            end_date = datetime.now().strftime("%Y-%m-%d")
            query_filter = {
                "_and": [
                    {"_gte": {"patent_date": last_run_date}},
                    {"_lte": {"patent_date": end_date}}
                ]
            }
            print(f"📅 Fetching patents since last run: {last_run_date} to {end_date}")
        else:
            print("⚠️ No previous run found, fetching last 7 days")
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            query_filter = {
                "_and": [
                    {"_gte": {"patent_date": start_str}},
                    {"_lte": {"patent_date": end_str}}
                ]
            }
            print(f"📅 Fetching patents from {start_str} to {end_str} (default 7 days)")
            
    elif args.days_back:
        # Fetch patents from N days ago to today
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(args.days_back))
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        query_filter = {
            "_and": [
                {"_gte": {"patent_date": start_str}},
                {"_lte": {"patent_date": end_str}}
            ]
        }
        print(f"📅 Fetching patents from {start_str} to {end_str} ({args.days_back} days)")
        
    elif args.start_date and args.end_date:
        # Custom date range
        query_filter = {
            "_and": [
                {"_gte": {"patent_date": args.start_date}},
                {"_lte": {"patent_date": args.end_date}}
            ]
        }
        print(f"📅 Fetching patents from {args.start_date} to {args.end_date}")
        
    elif args.start_date:
        # From start date to today
        from datetime import datetime
        end_date = datetime.now().strftime("%Y-%m-%d")
        query_filter = {
            "_and": [
                {"_gte": {"patent_date": args.start_date}},
                {"_lte": {"patent_date": end_date}}
            ]
        }
        print(f"📅 Fetching patents from {args.start_date} to {end_date}")
        
    else:
        # Default to year
        query_filter = {"patent_year": args.year}
        print(f"📅 Fetching patents for year {args.year}")
    
    # Set up query parameters - get all the fields you need
    query_params = {
        "f": ["patent_id", "patent_title", "patent_date", "inventors", "assignees", "cpc_current", "wipo"],
        "q": query_filter
    }
    
    print(f"🚀 Starting patent extraction")
    print(f"📡 API: {args.base_url}/{args.endpoint}")
    print(f"📁 Output: {args.output}")
    
    df = fetch_all_patents(
        base_url=args.base_url,
        endpoint=args.endpoint, 
        api_key=args.api_key,
        query_params=query_params,
        checkpoint_file=args.output,
        checkpoint_interval=args.checkpoint_interval
    )
    
    print(f"✅ Extraction complete: {len(df)} patents collected")
    
    # Save last run date for future monitoring
    if len(df) > 0:
        from datetime import datetime
        last_run_file = args.output.replace('.csv', '_last_run.txt')
        with open(last_run_file, 'w') as f:
            f.write(datetime.now().strftime("%Y-%m-%d"))
        print(f"💾 Last run date saved to {last_run_file}")


if __name__ == "__main__":
    main()