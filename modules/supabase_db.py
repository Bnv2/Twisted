import streamlit as st
import pandas as pd
from supabase import create_client, Client

class TwistedSupabase:
    def __init__(self):
        """Initialize Supabase connection"""
        self.url = st.secrets["SUPABASE_URL"]
        self.key = st.secrets["SUPABASE_ANON_KEY"]
        self.client: Client = create_client(self.url, self.key)
    
    def read_table(self, sheet_name):
        """
        Read table as DataFrame - EXACT REPLACEMENT for get_data()
        
        Maps your Google Sheets names to Supabase tables
        """
        # Exact mapping of your sheet names
        table_map = {
            "Staff": "staff",
            "Events": "events",
            "Event_Financials": "event_financials",
            "Event_Contacts": "event_contacts",
            "Logistics_Details": "logistics_details",
            "Event_Reports": "event_reports",
            "Inventory": "inventory",
            "Event_Sales": "event_sales",
            "Event_Staffing": "event_staffing",
            "Staff_Database": "staff_database"
        }
        
        actual_table = table_map.get(sheet_name, sheet_name.lower())
        
        try:
            response = self.client.table(actual_table).select("*").execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                # Convert column names to match Google Sheets format
                # Supabase uses lowercase_underscore, you use Title_Case
                column_name_map = {
                    # Staff
                    "email": "Email",
                    "name": "Name", 
                    "role": "Role",
                    "pin": "PIN",
                    "type": "Type",
                    "phone": "Phone",
                    "photo": "Photo",
                    
                    # Events
                    "event_id": "Event_ID",
                    "date": "Date",
                    "end_date": "End_Date",
                    "venue": "Venue",
                    "address": "Address",
                    "maps_link": "Maps_Link",
                    "status": "Status",
                    "is_multi_day": "Is_Multi_Day",
                    "contact_type": "Contact_Type",
                    "notes": "Notes",
                    "last_edited_by": "Last_Edited_By",
                    "organiser_name": "Organiser_Name",
                    "event_type": "Event_Type",
                    
                    # Financials
                    "rent": "Rent",
                    "rent_status": "Rent_Status",
                    "rent_paid_date": "Rent_Paid_Date",
                    "rent_due_date": "Rent_Due_Date",
                    "cleaning_deposit": "Cleaning_Deposit",
                    "deposit_paid": "Deposit_Paid",
                    "deposit_refunded": "Deposit_Refunded",
                    "fee_structure": "Fee_Structure",
                    "commission_rate": "Commission_Rate",
                    "deposit": "Deposit",
                    "payment_date": "Payment_Date",
                    "due_date": "Due_Date",
                    
                    # Contacts
                    "contact_id": "Contact_ID",
                    "preferred_method": "Preferred_Method",
                    "pref_method": "Pref_Method",
                    
                    # Logistics
                    "bump_in": "Bump_In",
                    "bump_out": "Bump_Out",
                    "setup_type": "Setup_Type",
                    "power": "Power",
                    "water": "Water",
                    "comments": "Comments",
                    
                    # Reports
                    "report_date": "Report_Date",
                    "weather": "Weather",
                    "time_leave": "Time_Leave",
                    "time_reach": "Time_Reach",
                    "other_stalls": "Other_Stalls",
                    "water_access": "Water_Access",
                    "power_access": "Power_Access",
                    "general_comments": "General_Comments",
                    
                    # Inventory
                    "item_name": "Item_Name",
                    "start_qty": "Start_Qty",
                    "end_qty": "End_Qty",
                    "sold_qty": "Sold_Qty",
                    "waste": "Waste",
                    
                    # Sales
                    "opening_float": "Opening_Float",
                    "cash_sales": "Cash_Sales",
                    "card_sales": "Card_Sales",
                    "closing_float": "Closing_Float",
                    "total_revenue": "Total_Revenue",
                    
                    # Staffing
                    "staff_name": "Staff_Name",
                    "start_time": "Start_Time",
                    "end_time": "End_Time",
                    "break_time": "Break_Time",
                    "payment_method": "Payment_Method",
                    "payment_status": "Payment_Status",
                    
                    # Staff Database
                    "hourly_rate": "Hourly_Rate",
                    "tfn": "TFN",
                    "photo_url": "Photo_URL",
                    "skills": "Skills",
                    "rating": "Rating"
                }
                
                # Rename columns to match your existing code
                df = df.rename(columns=column_name_map)
                
                # Remove internal columns that don't exist in Google Sheets
                columns_to_remove = ['id', 'created_at', 'updated_at']
                df = df.drop(columns=[col for col in columns_to_remove if col in df.columns], errors='ignore')
                
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error reading {sheet_name}: {e}")
            return pd.DataFrame()
    
    def update_table(self, sheet_name, dataframe):
        """
        Update table - EXACT REPLACEMENT for conn.update()
        """
        table_map = {
            "Staff": "staff",
            "Events": "events",
            "Event_Financials": "event_financials",
            "Event_Contacts": "event_contacts",
            "Logistics_Details": "logistics_details",
            "Event_Reports": "event_reports",
            "Inventory": "inventory",
            "Event_Sales": "event_sales",
            "Event_Staffing": "event_staffing",
            "Staff_Database": "staff_database"
        }
        
        actual_table = table_map.get(sheet_name, sheet_name.lower())
        
        try:
            # Convert Title_Case to lowercase_underscore for Supabase
            reverse_column_map = {
                # Staff
                "Email": "email",
                "Name": "name",
                "Role": "role",
                "PIN": "pin",
                "Type": "type",
                "Phone": "phone",
                "Photo": "photo",
                
                # Events
                "Event_ID": "event_id",
                "Date": "date",
                "End_Date": "end_date",
                "Venue": "venue",
                "Address": "address",
                "Maps_Link": "maps_link",
                "Status": "status",
                "Is_Multi_Day": "is_multi_day",
                "Contact_Type": "contact_type",
                "Notes": "notes",
                "Last_Edited_By": "last_edited_by",
                "Organiser_Name": "organiser_name",
                "Event_Type": "event_type",
                
                # Financials
                "Rent": "rent",
                "Rent_Status": "rent_status",
                "Rent_Paid_Date": "rent_paid_date",
                "Rent_Due_Date": "rent_due_date",
                "Cleaning_Deposit": "cleaning_deposit",
                "Deposit_Paid": "deposit_paid",
                "Deposit_Refunded": "deposit_refunded",
                "Fee_Structure": "fee_structure",
                "Commission_Rate": "commission_rate",
                "Deposit": "deposit",
                "Payment_Date": "payment_date",
                "Due_Date": "due_date",
                
                # Contacts
                "Contact_ID": "contact_id",
                "Preferred_Method": "preferred_method",
                "Pref_Method": "pref_method",
                
                # Logistics
                "Bump_In": "bump_in",
                "Bump_Out": "bump_out",
                "Setup_Type": "setup_type",
                "Power": "power",
                "Water": "water",
                "Comments": "comments",
                
                # Reports
                "Report_Date": "report_date",
                "Weather": "weather",
                "Time_Leave": "time_leave",
                "Time_Reach": "time_reach",
                "Other_Stalls": "other_stalls",
                "Water_Access": "water_access",
                "Power_Access": "power_access",
                "General_Comments": "general_comments",
                
                # Inventory
                "Item_Name": "item_name",
                "Start_Qty": "start_qty",
                "End_Qty": "end_qty",
                "Sold_Qty": "sold_qty",
                "Waste": "waste",
                
                # Sales
                "Opening_Float": "opening_float",
                "Cash_Sales": "cash_sales",
                "Card_Sales": "card_sales",
                "Closing_Float": "closing_float",
                "Total_Revenue": "total_revenue",
                
                # Staffing
                "Staff_Name": "staff_name",
                "Start_Time": "start_time",
                "End_Time": "end_time",
                "Break_Time": "break_time",
                "Payment_Method": "payment_method",
                "Payment_Status": "payment_status",
                
                # Staff Database
                "Hourly_Rate": "hourly_rate",
                "TFN": "tfn",
                "Photo_URL": "photo_url",
                "Skills": "skills",
                "Rating": "rating"
            }
            
            # Rename columns for Supabase
            df = dataframe.rename(columns=reverse_column_map)
            
            # Convert to list of dicts
            records = df.to_dict('records')
            
            # Clear table (matching Google Sheets behavior)
            self.client.table(actual_table).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            
            # Insert in batches of 100
            for i in range(0, len(records), 100):
                batch = records[i:i+100]
                self.client.table(actual_table).insert(batch).execute()
            
            return True
            
        except Exception as e:
            st.error(f"Error updating {sheet_name}: {e}")
            return False


# ==========================================
# CACHED CONNECTION
# ==========================================
@st.cache_resource
def get_supabase():
    """Singleton Supabase connection for Streamlit"""
    return TwistedSupabase()

db = get_supabase()
