const f = (firstName) => {
  const promise = new Promise((resolve, reject) => {
    setTimeout(() => {
      if (!firstName) return reject(new Error("firstName is required"));
      const fullName = `${firstName} Smith`;
      resolve(fullName);
    }, 2000);
  });
};
