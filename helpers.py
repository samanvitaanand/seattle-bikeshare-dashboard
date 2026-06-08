import pandas as pd
import folium
import plotly.express as px

#load files
def load_data():
    station = pd.read_csv("archive/station.csv")
    trip = pd.read_csv("archive/trip.csv", on_bad_lines='skip')
    weather = pd.read_csv("archive/weather.csv")
    return station, trip, weather



# page 1

def create_station_map(station):
    m = folium.Map(location=[station['lat'].mean(), station['long'].mean()], zoom_start=13)
    
    for _, row in station.iterrows():
        popup_text = f"""
        <b>{row['name']}</b><br>
        Docks: {row['current_dockcount']}<br>
        Installed: {row['install_date']}<br>
        Station ID: {row['station_id']}
        """
        folium.CircleMarker(
            location=[row['lat'], row['long']],
            radius=6,
            color='blue',
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=200)
        ).add_to(m)
    
    return m


#page 2

def plot_busiest_stations(trip):
    top_stations = trip['from_station_name'].value_counts().head(10).reset_index()
    top_stations.columns = ['Station', 'Trips']
    fig = px.bar(top_stations, x='Trips', y='Station', orientation='h',
                 title='Top 10 Busiest Stations', color='Trips',
                 color_continuous_scale='Blues')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


def plot_popular_routes(trip):
    trip['route'] = trip['from_station_name'] + ' → ' + trip['to_station_name']
    top_routes = trip['route'].value_counts().head(10).reset_index()
    top_routes.columns = ['Route', 'Trips']
    fig = px.bar(top_routes, x='Trips', y='Route', orientation='h',
                 title='Top 10 Most Popular Routes', color='Trips',
                 color_continuous_scale='Greens')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


def plot_usertype(trip):
    usertype = trip['usertype'].value_counts().reset_index()
    usertype.columns = ['User Type', 'Trips']
    fig = px.pie(usertype, values='Trips', names='User Type',
                 title='Member vs Casual Riders',
                 color_discrete_sequence=px.colors.sequential.Blues_r)
    return fig


def plot_gender(trip):
    gender = trip['gender'].value_counts().reset_index()
    gender.columns = ['Gender', 'Trips']
    fig = px.pie(gender, values='Trips', names='Gender',
                 title='Trips by Gender',
                 color_discrete_sequence=px.colors.sequential.Greens_r)
    return fig

# def plot_age_distribution(trip):
#     trip = trip.dropna(subset=['birthyear'])
#     trip['age'] = 2014 - trip['birthyear']
#     trip = trip[(trip['age'] > 10) & (trip['age'] < 80)]
#     fig = px.histogram(trip, x='age', nbins=30,
#                        title='Age Distribution of Riders',
#                        color_discrete_sequence=px.colors.sequential.Rainbow) # Plasma, Turbo, Viridis, or Rainbow
#     fig.update_layout(xaxis_title='Age', yaxis_title='Count')
#     return fig

#gradient one
def plot_age_distribution(trip):
    trip = trip.dropna(subset=['birthyear'])
    trip['age'] = 2014 - trip['birthyear']
    trip = trip[(trip['age'] > 10) & (trip['age'] < 80)]
    counts, bins = pd.cut(trip['age'], bins=30, retbins=True)
    bin_counts = counts.value_counts().sort_index().reset_index()
    bin_counts.columns = ['Age Range', 'Count']
    bin_counts['Age'] = [round((interval.left + interval.right) / 2) for interval in bin_counts['Age Range']]
    fig = px.bar(bin_counts, x='Age', y='Count',
                 title='Age Distribution of Riders',
                 color='Count',
                 color_continuous_scale='Viridis')
    fig.update_layout(xaxis_title='Age', yaxis_title='Count')
    return fig



# page 3

def prepare_weather_ridership(trip, weather):
    # Convert the date columns to the same format so we can merge them
    trip['date'] = pd.to_datetime(trip['starttime']).dt.date
    weather['date'] = pd.to_datetime(weather['Date']).dt.date
    
    # Count the number of trips per day
    daily_trips = trip.groupby('date').size().reset_index(name='trip_count')
    
    # Merge trip counts with weather data on the date column
    merged = pd.merge(daily_trips, weather, on='date', how='inner')
    
    return merged

def plot_temp_vs_ridership(merged):
    # Scatter plot — each dot is one day
    # x = temperature, y = number of trips that day
    fig = px.scatter(merged, x='Mean_Temperature_F', y='trip_count',
                     title='Temperature vs Daily Ridership',
                     labels={'Mean_Temperature_F': 'Mean Temperature (°F)', 'trip_count': 'Number of Trips'},
                     color='trip_count',
                     color_continuous_scale='Reds',
                     trendline='ols')  # adds a trend line
    return fig

def plot_rain_vs_ridership(merged):
    # Add a column labeling each day as rainy or not
    merged['weather_event'] = merged['Events'].fillna('None')
    
    # Box plot showing trip distribution for each weather type
    fig = px.box(merged, x='weather_event', y='trip_count',
                 title='Ridership by Weather Event',
                 labels={'weather_event': 'Weather', 'trip_count': 'Number of Trips'},
                 color='weather_event')
    return fig


def plot_ridership_over_time(merged):
    # Line chart showing total trips per day over the entire dataset
    fig = px.line(merged, x='date', y='trip_count',
                  title='Daily Ridership Over Time',
                  labels={'date': 'Date', 'trip_count': 'Number of Trips'},
                  color_discrete_sequence=['#1f77b4'])
    
    # Add a smoothed average line on top
    fig.add_scatter(x=merged['date'], 
                    y=merged['trip_count'].rolling(7).mean(),
                    name='7-day average',
                    line=dict(color='red', width=2))
    return fig


# page 4
def plot_top_destinations(trip, station_name):
    # Filter trips that started at the selected station
    filtered = trip[trip['from_station_name'] == station_name]
    
    # Count trips to each destination
    destinations = filtered['to_station_name'].value_counts().head(10).reset_index()
    destinations.columns = ['Destination', 'Trips']
    
    fig = px.bar(destinations, x='Trips', y='Destination', orientation='h',
                 title=f'Top Destinations from {station_name}',
                 color='Trips', color_continuous_scale='Blues')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


def plot_busiest_hours(trip, station_name):
    # Filter trips that started at the selected station
    filtered = trip[trip['from_station_name'] == station_name]
    
    # Extract the hour from the start time
    filtered['hour'] = pd.to_datetime(filtered['starttime']).dt.hour
    
    # Count trips per hour
    hourly = filtered.groupby('hour').size().reset_index(name='trip_count')
    
    fig = px.bar(hourly, x='hour', y='trip_count',
                 title=f'Busiest Hours at {station_name}',
                 labels={'hour': 'Hour of Day', 'trip_count': 'Number of Trips'},
                 color='trip_count', color_continuous_scale='Oranges')
    return fig