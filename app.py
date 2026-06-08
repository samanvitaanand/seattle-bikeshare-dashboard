from helpers import *
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Seattle Bike Share Explorer",
    page_icon="🚲",
    layout="wide"
)

# st.title("Seattle Bike Share Explorer")
# st.markdown("An interactive look at Seattle's bike share network.")

station, trip, weather = load_data()

st.sidebar.title("Seattle Bike Share")
st.sidebar.markdown("Exploring Pronto bike share data from 2014-2016.")
st.sidebar.divider()
page = st.sidebar.radio("Go to", ["Home", "Station Map", "Trip Explorer", "Weather vs Ridership", "Station Deep Dive"]) 
# st.sidebar.title("Navigation")
# page = st.sidebar.radio("Go to", ["Home", "Station Map", "Trip Explorer", "Weather vs Ridership", "Station Deep Dive"])

if page == "Home":
    st.title("Seattle Bike Share Explorer")
    st.markdown("An interactive dashboard exploring Seattle's Pronto bike share network from 2014–2016.")
    
    st.divider()
    
    # Row 1 — key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Trips", f"{len(trip):,}")
    with col2:
        st.metric("Total Stations", f"{len(station):,}")
    with col3:
        avg_duration = round(trip['tripduration'].mean() / 60, 1)
        st.metric("Avg Trip Duration", f"{avg_duration} mins")
    
    # Row 2 — more metrics
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Member Trips", f"{len(trip[trip['usertype'] == 'Member']):,}")
    with col5:
        st.metric("Casual Trips", f"{len(trip[trip['usertype'] == 'Casual Rider']):,}")
    with col6:
        st.metric("Weather Records", f"{len(weather):,} days")
    
    st.divider()
    st.markdown("### About this project")
    st.markdown("This dashboard was built using Python, Streamlit, and Plotly. Use the sidebar to explore station locations, trip patterns, weather impacts, and individual station breakdowns.")

elif page == "Station Map":
    st.title("Station Map")
    st.markdown("An interactive look at Seattle's bike share network.")
    m = create_station_map(station)
    st_folium(m, width=900, height=500)

# elif page == "Trip Explorer":
#     # st.title("Trip Explorer")
#     # st.markdown("Explore bike share trip patterns across Seattle.")
#     # st.plotly_chart(plot_busiest_stations(trip), use_container_width=True)
#     # st.plotly_chart(plot_popular_routes(trip), use_container_width=True)


#     # avg_duration = round(trip['tripduration'].mean() / 60, 1)
#     # st.metric(label="Average Trip Duration", value=f"{avg_duration} mins")
#     # st.plotly_chart(plot_usertype(trip), use_container_width=True)

#     st.title("Trip Explorer")
#     st.markdown("Explore bike share trip patterns across Seattle.")

#     avg_duration = round(trip['tripduration'].mean() / 60, 1)
#     st.metric(label="Average Trip Duration", value=f"{avg_duration} mins")
        
#     st.plotly_chart(plot_busiest_stations(trip), use_container_width=True)
#     st.caption("The top 10 stations with the most trip departures. These are the most active hubs in the network.")

#     st.plotly_chart(plot_usertype(trip), use_container_width=True)
#     st.caption("Members are annual subscribers. Casual riders use single-ride or short-term passes.")

#     st.plotly_chart(plot_gender(trip), use_container_width=True)
#     st.caption("Gender breakdown of riders who provided the information at registration.")

#     st.plotly_chart(plot_age_distribution(trip), use_container_width=True)
#     st.caption("Age distribution calculated from birth year. Most riders are between 25 and 40 years old.")

#     st.plotly_chart(plot_popular_routes(trip), use_container_width=True)
#     st.caption("The most frequently taken station-to-station routes, including round trips back to the same station.")

elif page == "Trip Explorer":
    st.title("Trip Explorer")
    st.markdown("Explore bike share trip patterns across Seattle.")

    # --- Filters in the sidebar ---
    st.sidebar.divider()
    st.sidebar.markdown("### Filters")
    
    # User type filter
    user_types = ['All'] + list(trip['usertype'].dropna().unique())
    selected_user = st.sidebar.selectbox("User Type", user_types)
    
    # Gender filter
    genders = ['All'] + list(trip['gender'].dropna().unique())
    selected_gender = st.sidebar.selectbox("Gender", genders)
    
    # Apply filters to the trip data
    filtered_trip = trip.copy()
    if selected_user != 'All':
        filtered_trip = filtered_trip[filtered_trip['usertype'] == selected_user]
    if selected_gender != 'All':
        filtered_trip = filtered_trip[filtered_trip['gender'] == selected_gender]
    
    # Show how many trips match the current filters
    st.caption(f"Showing {len(filtered_trip):,} trips based on current filters.")

    avg_duration = round(filtered_trip['tripduration'].mean() / 60, 1)
    st.metric(label="Average Trip Duration", value=f"{avg_duration} mins")
    st.caption("Average duration across all filtered trips.")

    st.plotly_chart(plot_busiest_stations(filtered_trip), use_container_width=True)
    st.caption("The top 10 stations with the most trip departures. These are the most active hubs in the network.")

    st.plotly_chart(plot_usertype(filtered_trip), use_container_width=True)
    st.caption("Members are annual subscribers. Casual riders use single-ride or short-term passes.")

    st.plotly_chart(plot_gender(filtered_trip), use_container_width=True)
    st.caption("Gender breakdown of riders who provided the information at registration.")

    st.plotly_chart(plot_age_distribution(filtered_trip), use_container_width=True)
    st.caption("Age distribution calculated from birth year. Most riders are between 25 and 40 years old.")

    st.plotly_chart(plot_popular_routes(filtered_trip), use_container_width=True)
    st.caption("The most frequently taken station-to-station routes, including round trips back to the same station.")



elif page == "Weather vs Ridership":
    st.title("Weather vs Ridership")
    st.markdown("How does Seattle weather affect bike share usage?")
    
    # Prepare the merged dataset
    merged = prepare_weather_ridership(trip, weather)
    
    # Show the two charts stacked
    st.plotly_chart(plot_temp_vs_ridership(merged), use_container_width=True)
    st.caption("Each dot represents one day. The trendline shows that warmer days consistently attract more riders.")

    st.plotly_chart(plot_rain_vs_ridership(merged), use_container_width=True)
    st.caption("Box plots show the spread of daily trips for each weather condition. Rainy and foggy days tend to have fewer riders.")

    st.plotly_chart(plot_ridership_over_time(merged), use_container_width=True)
    st.caption("Blue = actual daily trips. Red = 7-day rolling average. Notice how ridership peaks in spring and summer and drops in winter.")


elif page == "Station Deep Dive":
    st.title("Station Deep Dive")
    st.markdown("Select a station to explore its trip patterns.")
    
    # Dropdown to pick a station
    station_name = st.selectbox("Choose a station", sorted(trip['from_station_name'].unique()))
    
    st.plotly_chart(plot_top_destinations(trip, station_name), use_container_width=True)
    st.caption("The top 10 most common destinations for trips starting at this station.")
    
    st.plotly_chart(plot_busiest_hours(trip, station_name), use_container_width=True)
    st.caption("Number of trips departing from this station by hour of day.")
