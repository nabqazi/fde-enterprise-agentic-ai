// Deliberately flawed JavaScript — demo fixture, not production code.
// Three distinct flaws for the reviewer to find.

// Flaw 1 (error-handling): missing await + bare catch swallows all errors
async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        const data = response.json();  // missing await — returns a Promise, not data
        return data;
    } catch (e) {
        // bare catch: swallows network errors, parse errors, and 4xx/5xx silently
    }
}

// Flaw 2 (cohesion + correctness): three responsibilities and an off-by-one
function processUsers(users) {
    // filter, mutate, and log all in one function (cohesion)
    const active = users.filter(u => u.status == "active");  // == not ===

    for (var i = 0; i <= active.length; i++) {  // off-by-one: <= should be <
        active[i].score = active[i].score + 1;  // throws on last iteration
    }

    console.log("Done:", active);
    return active;
}

// Flaw 3 (naming): misleading name hides linear scan on every call
function getUserById(users, id) {
    for (var i = 0; i < users.length; i++) {
        if (users[i].id == id) {
            return users[i];
        }
    }
    return null;
}
