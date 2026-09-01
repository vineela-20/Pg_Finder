import streamlit as st
from pincode_tool import search_google_maps
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="PG & Hotel Finder",
    page_icon="🏨"
)

st.title("🏨 PG & Hotel Finder")
st.write("Enter a pincode to find PGs and hotels in that location.")

pincode = st.text_input(
    "Enter Pincode",
    placeholder="Example: 500001"
)

if st.button("🔍 Search"):

    if not pincode:
        st.error("Please enter a pincode.")

    elif not pincode.isdigit() or len(pincode) != 6:
        st.error("Please enter a valid 6-digit pincode.")

    else:

        with st.spinner("Searching Google Maps..."):

            results = search_google_maps(pincode)

        if results:

            # -----------------------------------------
            # TOTAL COUNT
            # -----------------------------------------

            total_results = len(results)

            st.success(
                f"Total {total_results} PGs/Hotels found in {pincode}."
            )

            # -----------------------------------------
            # CONVERT RESULTS INTO LIST
            # -----------------------------------------

            display_results = []

            for result in results.values():

                display_result = {
                    "Website": result.get("Website", ""),
                    "Name of PG": result.get("Name", ""),
                    "Phone Number": result.get("Phone", ""),
                    "Rating": result.get("Rating", ""),
                    "Address": result.get("Address", "")
                }

                display_results.append(display_result)

            # -----------------------------------------
            # SHOW ONLY TOP 10 ON UI
            # -----------------------------------------

            st.subheader("Top 10 Results")

            top_10_results = display_results[:10]

            for index, result in enumerate(
                top_10_results,
                start=1
            ):

                st.markdown(
                    f"### {index}. {result['Name of PG']}"
                )

                st.write(
                    f"📞 **Phone:** {result['Phone Number']}"
                )

                st.write(
                    f"⭐ **Rating:** {result['Rating']}"
                )

                st.write(
                    f"🌐 **Website:** {result['Website']}"
                )

                st.write(
                    f"📍 **Address:** {result['Address']}"
                )

                st.divider()

            # -----------------------------------------
            # EXCEL DOWNLOAD - ALL RESULTS
            # -----------------------------------------

            df = pd.DataFrame(display_results)

            # Put columns in desired order
            df = df[
                [
                    "Website",
                    "Name of PG",
                    "Phone Number",
                    "Rating",
                    "Address"
                ]
            ]

            # Create Excel file in memory
            excel_buffer = BytesIO()

            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:

                df.to_excel(
                    writer,
                    index=False,
                    sheet_name="PG Results"
                )

            excel_buffer.seek(0)

            # -----------------------------------------
            # DOWNLOAD BUTTON
            # -----------------------------------------

            st.download_button(
                label="📥 Download All Results as Excel",
                data=excel_buffer,
                file_name=f"pg_results_{pincode}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        else:

            st.warning(
                f"No PGs or hotels found for pincode {pincode}."
            )