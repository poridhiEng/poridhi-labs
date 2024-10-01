const { kafka } = require("./client");

async function init() {
  const admin = kafka.admin();
  console.log("Admin connecting...");
  admin.connect();
  console.log("Adming Connection Success...");

  console.log("Creating Topic [riders_update]");
  await admin.createTopics({
    topics: [
      {
        topic: "riders_update",
        numPartitions: 2,
      },
    ],
  });
  console.log("Topic Created Success [riders_update]");

  console.log("Disconnecting Admin..");
  await admin.disconnect();
}

init();