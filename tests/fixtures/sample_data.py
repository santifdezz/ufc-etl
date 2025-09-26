"""Sample data for testing."""

SAMPLE_FIGHTER_HTML = """
<table class="b-statistics__table">
    <tr class="b-statistics__table-row">
        <td><a href="/fighter-details/123abc">John Doe</a></td>
        <td>John</td>
        <td>Doe</td>
        <td>"The Test"</td>
        <td>6' 0"</td>
        <td>185 lbs.</td>
        <td>74"</td>
        <td>Orthodox</td>
        <td>10</td>
        <td>2</td>
        <td>0</td>
    </tr>
</table>
"""

SAMPLE_EVENT_HTML = """
<table class="b-statistics__table-events">
    <tr>
        <th>Name/Date</th>
        <th>Location</th>
    </tr>
    <tr>
        <td>
            <i class="b-statistics__table-content">
                <a href="/event-details/test123">UFC Test Event</a>
                <span class="b-statistics__date">December 01, 2023</span>
            </i>
        </td>
        <td>Las Vegas, Nevada, USA</td>
    </tr>
</table>
"""

SAMPLE_FIGHT_DETAILS_HTML = """
<div class="b-fight-details">
    <h2 class="b-content__title">
        <a href="/event-details/event123">UFC Test Event</a>
    </h2>
    <div class="b-fight-details__person">
        <h3 class="b-fight-details__person-name">
            <a href="/fighter-details/fighter1">Fighter One</a>
        </h3>
        <i class="b-fight-details__person-status green"></i>
    </div>
    <div class="b-fight-details__person">
        <h3 class="b-fight-details__person-name">
            <a href="/fighter-details/fighter2">Fighter Two</a>
        </h3>
        <i class="b-fight-details__person-status"></i>
    </div>
    <i class="b-fight-details__fight-title">Lightweight Bout</i>
</div>
"""