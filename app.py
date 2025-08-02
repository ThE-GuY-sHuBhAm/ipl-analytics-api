from flask import Flask, jsonify, request, Response, render_template
import ipl

app = Flask(__name__)

@app.route('/')
def home():
    """
    Serves the main HTML page for the user interface.
    """
    return render_template('index.html')

@app.route('/api/list-all')
def list_all():
    """
    Provides sorted lists of all unique batters, bowlers, and teams.
    """
    batters = sorted(list(ipl.ball_with_match_df['batter'].unique()))
    bowlers = sorted(list(ipl.ball_with_match_df['bowler'].unique()))
    teams = sorted(list(ipl.ALL_TEAMS))
    return jsonify({"batters": batters, "bowlers": bowlers, "teams": teams})

#Main API Routes

@app.route('/api/teamvteam')
def teamvteam():
    """
    Provides head-to-head stats for a match-up between two teams.
    """
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    if not team1 or not team2:
        return jsonify({"error": "Both 'team1' and 'team2' parameters are required."}), 400
    response_data = ipl.teamVteamAPI(team1, team2)
    return jsonify(response_data)

@app.route('/api/batting-record')
def batting_record():
    """
    Provides a comprehensive batting report for a single player.
    """
    batsman_name = request.args.get('batsman', '').strip()
    if not batsman_name:
        return jsonify({"error": "The 'batsman' parameter is required."}), 400
    response_data = ipl.batsmanAPI(batsman_name)
    return Response(response_data, mimetype='application/json')

@app.route('/api/bowling-record')
def bowling_record():
    """
    Provides a comprehensive bowling report for a single player.
    """
    bowler_name = request.args.get('bowler', '').strip()
    if not bowler_name:
        return jsonify({"error": "The 'bowler' parameter is required."}), 400
    response_data = ipl.bowlerAPI(bowler_name)
    return Response(response_data, mimetype='application/json')


@app.errorhandler(404)
def not_found(error):
    """
    Handles 404 Not Found errors with a JSON response.
    """
    return jsonify({"error": "Not Found", "message": "The requested URL was not found on the server."}), 404


if __name__ == '__main__':
    app.run(debug=True)

