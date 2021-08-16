defmodule PolitiTweet.Twitter.Api do
  use HTTPoison.Base

  def process_request_url(url) do
    "https://api.twitter.com/2" <> url
  end

  def process_response_body(body) do
    body
    |> Jason.decode!()
  end

  defmodule User do
    defstruct [
      :username,
      :id,
      :profile_image_url,
      :name,
      :protected,
      :created_at,
      :url,
      :public_metrics,
      :entities,
      :verified,
      :location
    ]
  end

  defp main_user_id, do: Application.get_env(:polititweet, PolitiTweet.Twitter.Api)[:main_user_id]

  defp bearer_tokens,
    do: Application.get_env(:polititweet, PolitiTweet.Twitter.Api)[:bearer_tokens]

  defp get_auth_headers do
    [Authorization: "Bearer #{Enum.random(bearer_tokens())}"]
  end

  @doc """
  Returns a list of all the tracked users on PolitiTweet.
  """
  def tracked_users(next_token \\ nil) do
    params_base = [
      max_results: 1000,
      "user.fields":
        [
          "created_at",
          "description",
          "entities",
          "id",
          "location",
          "name",
          "pinned_tweet_id",
          "profile_image_url",
          "protected",
          "public_metrics",
          "url",
          "username",
          "verified",
          "withheld"
        ]
        |> Enum.join(",")
    ]

    params = params_base ++ if next_token == nil, do: [], else: [pagination_token: next_token]

    case get("/users/#{main_user_id()}/following", get_auth_headers(), params: params) do
      {:ok, %HTTPoison.Response{status_code: 200, body: body}} ->
        users =
          body["data"]
          |> Stream.map(&Map.new(&1, fn {k, v} -> {String.to_atom(k), v} end))
          |> Enum.map(&Map.merge(%User{}, &1))

        case Map.get(body, "meta") do
          %{"next_token" => token} -> users ++ tracked_users(token)
          _ -> users
        end

      {:error, %HTTPoison.Error{reason: reason}} ->
        IO.inspect(reason)
        []
    end
  end
end
