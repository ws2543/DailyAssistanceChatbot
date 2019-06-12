
exports.handler = (event, context, callback) => {
	var start = event.currentIntent.slots.Start;
	var end = event.currentIntent.slots.End;
	var phone = event.currentIntent.slots.Phone;
	var userId = event.userId;

	var AWS = require('aws-sdk');

	AWS.config.update({region: "us-east-1"});

	var sqs = new AWS.SQS({apiVersion: '2012-11-05'});
	var params = {
		DelaySeconds: 10,
		MessageAttributes: {
			"Start": {
				DataType: "String",
				StringValue: start
			},
			"End": {
				DataType: "String",
				StringValue: end
			},
			"Phone": {
				DataType: "String",
				StringValue: phone
			},
			"userId": {
				DataType: "String",
				StringValue:userId
			}

		},

		MessageBody: "Information about this message.",
		QueueUrl: "<QUEUE-URL>"

	};

	sqs.sendMessage(params, function(err, data) {

		console.log("add it");

		if (err) {
			console.log("Error", err);
		} else {
			console.log("Success!", data.MessageId);
		}


	});

	var response = {"dialogAction": {
        "type": "Close",
        "fulfillmentState": "Fulfilled",
        "message": {
          "contentType": "PlainText",
          "content": "Got it! I will help you remind this and add it to the schedule!"
        }}};

	callback(null, response);







};