# import streamlit as st
# import pandas as pd
# import square.client # We will use the most stable import method
# from square.client import Client

# def render_sales_tab(eid, event_core, df_sales, df_fin, conn):
#     st.subheader("💰 Event Financial Performance")

#     # 1. INITIALIZE SQUARE
#     try:
#         # Using the direct class reference
#         square_client = Client(
#             access_token=st.secrets["SQUARE_ACCESS_TOKEN"],
#             environment='production'
#         )
#     except Exception as e:
#         st.error(f"Square SDK Initialization Failed: {e}")
#         return # Stop rendering if Square fails

#     # ⚠️ REPLACE WITH YOUR ACTUAL ID
#     MY_SQUARE_LOCATION_ID = "PASTE_YOUR_LOCATION_ID_HERE"

#     # 2. DATA PREP
#     # Pull current sales for this event
#     if not df_sales.empty and 'Event_ID' in df_sales.columns:
#         sales_match = df_sales[df_sales['Event_ID'] == eid]
#         curr_sales = sales_match.iloc[0] if not sales_match.empty else {}
#     else:
#         curr_sales = {}

#     # 3. SQUARE SYNC SECTION
#     with st.container(border=True):
#         sc1, sc2 = st.columns([3, 1])
#         sc1.markdown("### 🚀 Square POS Sync")
        
#         if sc2.button("Sync Square Sales", key=f"sync_{eid}", use_container_width=True):
#             with st.spinner("Connecting to Square..."):
#                 try:
#                     e_date = str(event_core.get('Date', ''))
#                     # API call to Square
#                     result = square_client.payments.list_payments(
#                         begin_time=f"{e_date}T00:00:00Z",
#                         end_time=f"{e_date}T23:59:59Z",
#                         location_id=MY_SQUARE_LOCATION_ID
#                     )
                    
#                     if result.is_success():
#                         payments = result.body.get('payments', [])
#                         sq_total = sum(p['amount_money']['amount'] for p in payments if p['status'] == 'COMPLETED') / 100
#                         st.session_state[f"sq_sync_{eid}"] = sq_total
#                         st.success(f"Fetched ${sq_total:,.2f}")
#                     else:
#                         st.error(f"Square Error: {result.errors[0]['detail']}")
#                 except Exception as e:
#                     st.error(f"Sync failed: {e}")

#     st.divider()

#     # 4. ENTRY FORM
#     sync_val = st.session_state.get(f"sq_sync_{eid}", float(curr_sales.get('Card_Sales', 0)))

#     with st.form(key=f"sales_form_{eid}", border=True):
#         f1, f2, f3 = st.columns(3)
#         n_float = f1.number_input("Opening Float ($)", value=float(curr_sales.get('Opening_Float', 0)))
#         n_cash = f2.number_input("Cash Sales ($)", value=float(curr_sales.get('Cash_Sales', 0)))
#         n_card = f3.number_input("Card Sales (Square) ($)", value=float(sync_val))
        
#         n_closing = st.number_input("Actual Closing Float ($)", value=float(curr_sales.get('Closing_Float', 0)))
#         total_rev = n_cash + n_card

#         if st.form_submit_button("💾 Save Reconciliation", use_container_width=True):
#             new_row = {
#                 "Event_ID": eid, "Opening_Float": n_float, "Cash_Sales": n_cash,
#                 "Card_Sales": n_card, "Closing_Float": n_closing, "Total_Revenue": total_rev
#             }
#             # Remove old record and add new
#             df_sales = df_sales[df_sales['Event_ID'] != eid] if not df_sales.empty else df_sales
#             df_sales = pd.concat([df_sales, pd.DataFrame([new_row])], ignore_index=True)
#             conn.update(worksheet="Event_Sales", data=df_sales)
#             st.success("Saved!"); st.rerun()

#     # 5. FINANCIAL SUMMARY
#     if not df_fin.empty and 'Event_ID' in df_fin.columns:
#         fin_match = df_fin[df_fin['Event_ID'] == eid]
#         curr_fin = fin_match.iloc[0] if not fin_match.empty else {}
#     else:
#         curr_fin = {}

#     rent_val = float(curr_fin.get('Rent', 0))
#     m1, m2, m3 = st.columns(3)
#     m1.metric("Gross Revenue", f"${total_rev:,.2f}")
#     m2.metric("Rent", f"${rent_val:,.2f}")
#     m3.metric("Net Profit", f"${total_rev - rent_val:,.2f}")

