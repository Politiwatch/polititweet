defmodule Polititweet.TwitterTest do
  use Polititweet.DataCase

  alias Polititweet.Twitter

  describe "users" do
    alias Polititweet.Twitter.User

    import Polititweet.TwitterFixtures

    @invalid_attrs %{twitter_id: nil, username: nil}

    test "list_users/0 returns all users" do
      user = user_fixture()
      assert Twitter.list_users() == [user]
    end

    test "get_user!/1 returns the user with given id" do
      user = user_fixture()
      assert Twitter.get_user!(user.id) == user
    end

    test "create_user/1 with valid data creates a user" do
      valid_attrs = %{twitter_id: "some twitter_id", username: "some username"}

      assert {:ok, %User{} = user} = Twitter.create_user(valid_attrs)
      assert user.twitter_id == "some twitter_id"
      assert user.username == "some username"
    end

    test "create_user/1 with invalid data returns error changeset" do
      assert {:error, %Ecto.Changeset{}} = Twitter.create_user(@invalid_attrs)
    end

    test "update_user/2 with valid data updates the user" do
      user = user_fixture()
      update_attrs = %{twitter_id: "some updated twitter_id", username: "some updated username"}

      assert {:ok, %User{} = user} = Twitter.update_user(user, update_attrs)
      assert user.twitter_id == "some updated twitter_id"
      assert user.username == "some updated username"
    end

    test "update_user/2 with invalid data returns error changeset" do
      user = user_fixture()
      assert {:error, %Ecto.Changeset{}} = Twitter.update_user(user, @invalid_attrs)
      assert user == Twitter.get_user!(user.id)
    end

    test "delete_user/1 deletes the user" do
      user = user_fixture()
      assert {:ok, %User{}} = Twitter.delete_user(user)
      assert_raise Ecto.NoResultsError, fn -> Twitter.get_user!(user.id) end
    end

    test "change_user/1 returns a user changeset" do
      user = user_fixture()
      assert %Ecto.Changeset{} = Twitter.change_user(user)
    end
  end
end
