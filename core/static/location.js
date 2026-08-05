const map = L.map("map");

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        attribution:
            "&copy; OpenStreetMap contributors"
    }
).addTo(map);

navigator.geolocation.getCurrentPosition(function(position){

    const lat = position.coords.latitude;
    const lng = position.coords.longitude;

    map.setView(
        [lat, lng],
        15
    );

    L.marker(
        [lat, lng]
    )
    .addTo(map)
    .bindPopup("You");

    fetch(
        "/update-location/",
        {

            method: "POST",

            headers:{

                "Content-Type":"application/json",

                "X-CSRFToken":
                getCookie("csrftoken")

            },

            body:JSON.stringify({

                latitude:lat,
                longitude:lng

            })

        }
    );

});


FRIENDS.forEach(function(friend){

    if(
        friend.latitude &&
        friend.longitude
    ){

        L.marker([
            friend.latitude,
            friend.longitude
        ])
        .addTo(map)
        .bindPopup(friend.username);

    }

});


function getCookie(name){

    let cookieValue = null;

    if(document.cookie){

        const cookies =
        document.cookie.split(";");

        for(let cookie of cookies){

            cookie = cookie.trim();

            if(
                cookie.startsWith(
                    name + "="
                )
            ){

                cookieValue =
                decodeURIComponent(
                    cookie.substring(
                        name.length + 1
                    )
                );

            }

        }

    }

    return cookieValue;

}