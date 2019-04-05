"""
    cronjob: badges.py
    ==================

    Calculates new badges and assigns them to the respective user.
"""
import sqlite3 as lite

def assign_by_query (
        badge_internal_id,
        query_in_table,
        query,
        allow_multiple_associations=True,
        allow_duplicates=False
    ):
    """
        Assigns badges based on query results.
        Will execute :query: on database :query_in_table:.
          Expects query result format: userid, (optional) data
        Will (if enabled) perform these checks:
         - allow_multiple_associations: Discard entry if user has already this badge type
         - allow_duplicates: Discard entry if user has already this badget type and data
    """

    # Execute :query:
    con = lite.connect('databases/' + query_in_table + '.db')
    cur = con.cursor()
    cur.execute(query)
    all_possible_awardees = cur.fetchall()
    con.close()

    con = lite.connect('databases/user.db')
    cur = con.cursor()

    cur.execute("SELECT id FROM badges WHERE internal_id=?", (badge_internal_id,))
    badge_id = cur.fetchone()[0]

    for awardee in all_possible_awardees:
        if not allow_duplicates or not allow_multiple_associations:
            # Count limit exists:
            cur.execute("SELECT COUNT(*) FROM badge_associations WHERE badgeid=? AND userid=?", (badge_id,awardee[0]))

            _badge_award_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM badge_associations WHERE badgeid=? AND userid=? AND data=?", (badge_id,awardee[0], awardee[1]))

            _badge_equal_award_count = cur.fetchone()[0]

            # If count limit violated, skip this user
            if not allow_multiple_associations and _badge_award_count != 0 or not allow_duplicates and _badge_equal_award_count != 0:
                continue

        cur.execute("INSERT INTO badge_associations (badgeid, userid, data, given_date, recognized) VALUES (?, ?, ?, strftime('%s','now'), 0)", (badge_id,awardee[0], awardee[1]))

    con.commit()
    con.close()


# Badges assignment

## -- Course related badges --

assign_by_query("100-reputation",
    "user",
    "select id, Null FROM user WHERE reputation >= 100",
    False, False
)

assign_by_query("first-course-promise",
    "courses",
    "SELECT user_id, Null FROM commitments WHERE invalidated=0 GROUP BY user_id",
    False, False
)

assign_by_query("first-course-proposal",
    "courses",
    "SELECT proposer, Min(id) FROM proposals WHERE deleted=0 GROUP BY proposer",
    False, False
)

assign_by_query("first-course",
    "courses",
    "SELECT proposer, Min(id) FROM proposals WHERE deleted=0 AND courseid !=0 GROUP BY proposer",
    False, False
)

assign_by_query("lots-of-courses",
    "courses",
    "SELECT proposer, Null FROM proposals WHERE deleted=0 AND courseid !=0 GROUP BY proposer HAVING Count(*) >= 5",
    False, False
)

assign_by_query("first-course-completed",
    "courses",
    "SELECT proposals.proposer, Min(courses.id) FROM proposals, courses WHERE proposals.courseid=courses.id AND courses.state = 1 GROUP BY proposals.proposer",
    False, False
)

assign_by_query("course-user-small",
    "courses",
    "SELECT admins.userid, courses.id FROM courses, enrollments, enrollments AS admins WHERE courses.id=enrollments.courseid AND enrollments.permission < 3 AND courses.id=admins.courseid AND admins.permission >= 3 GROUP BY enrollments.courseid HAVING Count(*) >= 5",
    True, False
)

assign_by_query("course-user-medium",
    "courses",
    "SELECT admins.userid, courses.id FROM courses, enrollments, enrollments AS admins WHERE courses.id=enrollments.courseid AND enrollments.permission < 3 AND courses.id=admins.courseid AND admins.permission >= 3 GROUP BY enrollments.courseid HAVING Count(*) >= 40",
    True, False
)

assign_by_query("course-user-large",
    "courses",
    "SELECT admins.userid, courses.id FROM courses, enrollments, enrollments AS admins WHERE courses.id=enrollments.courseid AND enrollments.permission < 3 AND courses.id=admins.courseid AND admins.permission >= 3 GROUP BY enrollments.courseid HAVING Count(*) >= 100",
    True, False
)


assign_by_query("first-upvote",
    "forum",
    "SELECT user_id, Null FROM score_votes WHERE direction=1 GROUP BY user_id",
    False, False
)

assign_by_query("first-downvote",
    "forum",
    "SELECT user_id, Null FROM score_votes WHERE direction=-1 GROUP BY user_id",
    False, False
)

assign_by_query("lots-of-votes",
    "forum",
    "SELECT user_id, Null FROM score_votes GROUP BY user_id HAVING Count(*) >= 50",
    False, False
)


assign_by_query("post-score-small",
    "forum",
    "SELECT author, Null FROM articles WHERE score > 5 UNION SELECT author, Null FROM answers WHERE score > 5",
    True, False
)

assign_by_query("post-score-medium",
    "forum",
    "SELECT author, Null FROM articles WHERE score > 20 UNION SELECT author, Null FROM answers WHERE score > 20",
    True, False
)

assign_by_query("post-score-large",
    "forum",
    "SELECT author, Null FROM articles WHERE score > 50 UNION SELECT author, Null FROM answers WHERE score > 50",
    True, False
)


assign_by_query("first-question",
    "forum",
    "SELECT author, Null FROM articles WHERE score > 1 GROUP BY author",
    False, False
)

assign_by_query("lots-of-questions",
    "forum",
    "SELECT author, Null FROM articles WHERE score > 1 GROUP BY author HAVING Count(*) >= 5",
    False, False
)

assign_by_query("first-accept",
    "forum",
    "SELECT author, Null FROM articles WHERE score > 1 AND hasAcceptedAnswer = 1 GROUP BY author",
    False, False
)


assign_by_query("first-answer",
    "forum",
    "SELECT author, Null FROM answers WHERE score > 1 GROUP BY author",
    False, False
)

assign_by_query("lots-of-answers",
    "forum",
    "SELECT author, Null FROM answers WHERE score > 1 GROUP BY author HAVING Count(*) >= 5",
    False, False
)

assign_by_query("better-than-rivalry-answers",
    "forum",
    "SELECT tmp.author, Null FROM (SELECT answers.author AS author FROM answers, answers AS comp WHERE answers.articleID = comp.articleID AND answers.id != comp.id AND answers.isAcceptedAnswer = 1 GROUP BY answers.id) AS tmp GROUP BY tmp.author HAVING Count(*) >= 3",
    False, False
)

assign_by_query("election-finalist",
    "election",
    "SELECT nominations.candidate, elections.id FROM nominations, elections WHERE elections.state = 6 AND nominations.election_id = elections.id AND nominations.state >= 0",
    True, False
)

assign_by_query("election-voter",
    "election",
    "SELECT voter, Null FROM votes GROUP BY voter",
    False, False
)
