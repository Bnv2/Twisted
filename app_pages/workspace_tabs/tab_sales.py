import streamlit as st
import pandas as pd
import time

def render_sales_tab(eid, selected_report_date, db, get_data):
    """
    Modular Sales Tab for Event Workspace.
    Uses @st.fragment for snappy balancing calculations.
    """
    # 1. FETCH DATA
    @st.cache_data(ttl=600)
    def get_sales_data():
        return db.read_table("event_sales")

    df_master_events = get_data("Events") 
    df_sales_dest = get_sales_data()

    # Force column lowercase for reliability with SQL
    if not df_sales_dest.empty:
        df_sales_dest.columns = [str(c).lower().strip() for c in df_sales_dest.columns]
    else:
        df_sales_dest = pd.DataFrame(columns=['event_id', 'total_revenue', 'card_sales', 'cash_sales'])

    # Get Event Context
    event_info = df_master_events[df_master_events['Event_ID'].astype(str) == str(eid)]
    is_multi = str(event_info.iloc[0].get('Is_Multi_Day', 'No')) == "Yes" if not event_info.empty else False
    
    # --- METRICS ---
    # Current Day Total
    day_total = df_sales_dest[df_sales_dest['event_id'].astype(str) == str(eid)]['total_revenue'].sum()
    
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Today's Gross", f"${day_total:,.2f}")
    if is_multi:
        m_col2.metric("Event Total (to date)", f"${day_total:,.2f}")
    
    st.divider()

    # --- FORM STATE ---
    # We use session state to track the "Auto-fill" and form resets
    if "form_id" not in st.session_state: st.session_state.form_id = 0
    if "fill_val" not in st.session_state: st.session_state.fill_val = 0.0

    # --- THE FRAGMENT ---
    @st.fragment
    def render_sales_form():
        st.subheader(f"📝 Sales Entry: {selected_report_date.strftime('%d/%m/%Y')}")
        fid = st.session_state.form_id
        
        # 1. TOTAL PAYMENTS
        st.markdown("#### 1. Total Payments")
        p1, p2 = st.columns(2)
        v_card = p1.number_input("Card / Eftpos", min_value=0.0, step=1.0, key=f"eftpos_{fid}")
        v_cash = p2.number_input("Cash", min_value=0.0, step=1.0, key=f"cash_{fid}")
        
        t_gross = v_card + v_cash
        st.markdown(f"### Gross Total: :green[${t_gross:,.2f}]")
        st.divider()
        
        # 2. CATEGORY INPUTS
        st.markdown("#### 2. Categories")
        c1, c2, c3, c4 = st.columns(4)
        v_quick = c1.number_input("Quick", min_value=0.0, step=1.0, key=f"quick_{fid}")
        v_food = c2.number_input("Food", min_value=0.0, step=1.0, key=f"food_{fid}")
        v_drinks = c3.number_input("Drinks", min_value=0.0, step=1.0, key=f"drinks_{fid}")
        v_uncat = c4.number_input("Uncategorised", min_value=0.0, step=1.0, value=st.session_state.fill_val, key=f"uncat_{fid}")
        
        st.session_state.fill_val = v_uncat

        # 3. BALANCING LOGIC
        cat_sum = v_quick + v_food + v_drinks + v_uncat
        diff = t_gross - cat_sum
        
        st.divider()
        
        if abs(diff) > 0.01:
            b_col1, b_col2 = st.columns([2, 1])
            b_col1.warning(f"⚠️ **Remaining to balance: ${diff:,.2f}**")
            if diff > 0:
                if b_col2.button(f"Auto-Fill ${diff:,.0f}", use_container_width=True):
                    st.session_state.fill_val = float(v_uncat + diff)
                    st.rerun(scope="fragment")
        else:
            st.success("✅ Totals Balance Perfectly!")

        # 4. SAVE LOGIC
        if round(t_gross, 2) == round(cat_sum, 2) and t_gross > 0:
            if st.button("💾 Save Sales Record", use_container_width=True, type="primary"):
                new_row = {
                    "event_id": str(eid),
                    "card_sales": float(v_card),
                    "cash_sales": float(v_cash),
                    "total_revenue": float(t_gross),
                    "opening_float": 0.0,
                    "closing_float": 0.0
                }
                
                try:
                    if db.insert_row("event_sales", new_row):
                        # Increment form_id to clear all number_inputs
                        st.session_state.form_id += 1
                        st.session_state.fill_val = 0.0
                        st.cache_data.clear() 
                        st.success("✅ Saved!")
                        time.sleep(1)
                        st.rerun() 
                except Exception as e:
                    st.error(f"Error saving sales: {e}")

    # EXECUTE FRAGMENT
    render_sales_form()